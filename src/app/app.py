import streamlit as st
import requests
import pandas as pd
import json
import sys
import os
from urllib.parse import quote

# Add the src directory to the system path to access utility functions
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(src_dir)

from src.utils.utils import get_languages_from_df_column_names

st.title("Skill Description Translator")

if "sheet_column_pairs" not in st.session_state:
    st.session_state.sheet_column_pairs = []

uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])

if uploaded_file is not None:
    st.success("File uploaded successfully")

    excel_file = pd.ExcelFile(uploaded_file)
    all_languages = []

    def add_pair():
        st.session_state.sheet_column_pairs.append({"sheet": None, "column": None})

    # Display the sheet-column pairs
    for i, pair in enumerate(st.session_state.sheet_column_pairs):
        with st.expander(f"Sheet-Column Pair {i+1}", expanded=True):
            sheet_name = st.selectbox(f"Select a sheet for pair {i+1}", excel_file.sheet_names, key=f"sheet_{i}")
            if sheet_name:
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                column_name = st.selectbox(f"Select the description column for pair {i+1}", df.columns.tolist(), key=f"column_{i}")
                st.session_state.sheet_column_pairs[i]["sheet"] = sheet_name
                st.session_state.sheet_column_pairs[i]["column"] = column_name
                if not all_languages:
                    all_languages = get_languages_from_df_column_names(df)

    st.button("Add sheet-column pair", on_click=add_pair)
    
    if st.session_state.sheet_column_pairs:
        st.markdown("<h3>Selected Sheet-Column Pairs:</h3>", unsafe_allow_html=True)
        for i, pair in enumerate(st.session_state.sheet_column_pairs):
            st.write(f"**Pair {i+1}:** Sheet - {pair['sheet']}, Column - {pair['column']}")

    if all_languages:
        with st.expander(f"Languages", expanded=True):
            st.markdown("<h3>Select the languages to translate to:</h3>", unsafe_allow_html=True)
            selected_languages = []
            for lang in all_languages:
                if st.checkbox(lang, key=f"lang_{lang}"):
                    selected_languages.append(lang)

    if st.button("Translate"):
        with st.spinner('Translating...'):
            try:
                uploaded_file.seek(0)

                files = {"file": uploaded_file}
                data = {
                    "sheet_column_pairs": st.session_state.sheet_column_pairs,
                    "selected_languages": selected_languages
                }
                headers = {
                    "accept": "application/json",
                }

                jdata = json.dumps(data, indent=4)
                st.write("Data being sent to the backend:", jdata)

                response = requests.post("http://localhost:8000/api/translate/", headers=headers, files=files, data={"data": jdata})

                if response.status_code == 200:
                    st.success('File translated successfully')
                    translated_file_path = response.json().get("file_path")
                    print(translated_file_path)
                    if translated_file_path:
                        encoded_path = quote(translated_file_path)
                        st.markdown(f'<a href="http://localhost:8000/api/download/{encoded_path}" target="_blank">Download the translated file</a>', unsafe_allow_html=True)
                else:
                    st.error(f'Error in translation: {response.text}')
            except Exception as e:
                st.error(f"Error in translation: {str(e)}")
