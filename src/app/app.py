"""
This is the main Streamlit app that allows users to upload an Excel file, select the sheets and columns to translate,
 and the languages to translate to. The app then sends the data to the FastAPI server for translation and displays 
 the download link for the translated file.
"""

import json
import time
from typing import List
import sys
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st


API_HOST='127.0.0.1'
API_PORT=5000
API_BASE_URL=f'http://{API_HOST}:{API_PORT}'


# Add the src directory to the system path to access utility functions
def get_column_names_for_translation(df, pattern="(to translate)"):
    """
    Gets the column names that contain the pattern in the DataFrame.
    """
    return [col for col in df.columns if pattern in col]


def get_languages_from_df_column_names(df: pd.DataFrame) -> List[str]:
    """
    # Assumes that the column name is in the format: {language_code} description
    """
    return [col.replace(' description', '') for col in df.columns if ' description' in col]


def create_session_state():
    """
    This function creates the session state variables for the Streamlit app.
    """
    if "sheet_column_pairs" not in st.session_state:
        st.session_state.sheet_column_pairs = []

    if "all_languages_selected" not in st.session_state:
        st.session_state.all_languages_selected = False

    if "selected_languages" not in st.session_state:
        st.session_state.selected_languages = []

    if "API_APP" not in st.session_state:
        st.session_state.API_APP = None

    if "API_STARTED" not in st.session_state:
        st.session_state.API_STARTED = False


def column_selector(df, sheet_name, i):
    possible_column_names = get_column_names_for_translation(df)
    selected_columns = st.session_state.sheet_column_pairs[i]["columns"]
    for col in possible_column_names:
        if st.checkbox(col, key=f"{sheet_name}_column_{col}_{i}", value=col in selected_columns):
            if col not in selected_columns:
                selected_columns.append(col)
        else:
            if col in selected_columns:
                selected_columns.remove(col)


def select_sheet_column_pairs_and_get_languages(excel_file, uploaded_file):
    all_languages = []

    def add_pair():
        if possible_sheets:
            st.session_state.sheet_column_pairs.append({"sheet": None, "columns": []})
        else:
            st.warning("All sheets have been selected")

    # Display the sheet-column pairs
    possible_sheets = excel_file.sheet_names
    for i, pair in enumerate(st.session_state.sheet_column_pairs):
        with st.expander(f"Selected sheet {i+1}", expanded=True):
            sheet_name = st.selectbox(
                "**Select a sheet and column[s] to translate:**", 
                possible_sheets, 
                key=f"sheet_{i}"
            )
            if sheet_name:
                st.session_state.sheet_column_pairs[i]["sheet"] = sheet_name
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

                column_selector(df, sheet_name, i)

                if not all_languages:
                    all_languages = get_languages_from_df_column_names(df)
        possible_sheets = [sh for sh in possible_sheets if sh != sheet_name]

    st.button("Add a sheet name for translation", on_click=add_pair)
    return all_languages


def display_selected_sheet_column_pairs():
    if st.session_state.sheet_column_pairs:
        st.markdown("<h5>Selected Sheet-Column Pairs:</h5>", unsafe_allow_html=True)
        for i, pair in enumerate(st.session_state.sheet_column_pairs):
            st.write(f"**Pair {i+1}:** Sheet - {pair['sheet']}, Column - {pair['columns']}")


def select_languages(all_languages):
    with st.expander(f"Languages", expanded=True):
        st.markdown("<h4>Select the languages to translate to:</h4>", unsafe_allow_html=True)
        select_all = st.checkbox("**Select All**", key="select_all_languages")
        if select_all:
            st.session_state.all_languages_selected = True
            st.session_state.selected_languages = all_languages
        else:
            st.session_state.all_languages_selected = False
            st.session_state.selected_languages = []

        for lang in all_languages:
            if st.session_state.all_languages_selected:
                st.checkbox(lang, key=f"lang_{lang}", value=True, disabled=True)
            else:
                if st.checkbox(lang, key=f"lang_{lang}"):
                    if lang not in st.session_state.selected_languages:
                        st.session_state.selected_languages.append(lang)
                else:
                    if lang in st.session_state.selected_languages:
                        st.session_state.selected_languages.remove(lang)


def run_translation(uploaded_file):
    with st.spinner('Translating...'):
        try:
            uploaded_file.seek(0)

            files = {"file": uploaded_file}
            data = {
                "sheet_column_pairs": st.session_state.sheet_column_pairs,
                "selected_languages": st.session_state.selected_languages
            }
            headers = {
                "accept": "application/json",
            }

            jdata = json.dumps(data, indent=4)
            print("data to send:", jdata)

            response = requests.post(f"{API_BASE_URL}/translate", headers=headers, files=files, data={"data": jdata})

            if response.status_code == 200:
                st.success('File translated successfully')
                translated_file_path = response.json().get("file_path")
                print(translated_file_path)
                if translated_file_path:
                    encoded_path = quote(translated_file_path)
                    st.markdown(f'<a href="{API_BASE_URL}download/{encoded_path}" target="_blank">Download the translated file</a>', unsafe_allow_html=True)
            else:
                st.error(f'Error in translation: {response.text}')
        except Exception as e:
            st.error(f"Error in translation: {str(e)}")


def main():
    st.title("Translator App")

    st.write("This app helps you translate the text in an Excel file to multiple languages. You can select the sheets and columns to translate and the languages to translate to.")

    create_session_state()

    uploaded_file = st.file_uploader("**Choose an Excel file**", type=["xlsx"])

    if uploaded_file is not None:
        st.success("File uploaded successfully")
        excel_file = pd.ExcelFile(uploaded_file)

        st.markdown("<h4>Select Sheet[s] to Translate:</h4>", unsafe_allow_html=True)

        all_languages = select_sheet_column_pairs_and_get_languages(excel_file, uploaded_file)

        display_selected_sheet_column_pairs()

        if all_languages:
            select_languages(all_languages)

        if not st.session_state.API_STARTED:
            st.write("Starting the API server...")
            if st.button("🚀  Translate"):

                import subprocess
                import threading

                def start_api(job):
                    print(f"Starting API server: {job}")
                    proc = subprocess.Popen(job)
                    proc.wait()
                    return proc
                
                job = [f'{sys.executable}', 'src/bootstrapper.py', API_HOST, str(API_PORT)]

                # server thread remains alive as long as the main thread is alive, or is manually killed
                thread = threading.Thread(name="fastapi_translation_bootstrapper", target=start_api, args=(job,), daemon=True)
                thread.start()

                time.sleep(2)
                run_translation(uploaded_file)

                st.session_state.API_STARTED = True

                st.rerun()

        if st.session_state.API_STARTED:
            st.write("Data being sent to the backend:")
            c1, c2, _, c4 = st.columns([1,1,1,1])
            with c4:
                if st.button("🔥  Shutdown"):
                    response = requests.get(f"{API_BASE_URL}/shutdown")
                    st.session_state.API_STARTED = False
                    st.rerun()


if __name__ == "__main__":
    main()
