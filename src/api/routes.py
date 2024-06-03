from typing import List, Dict
from io import BytesIO
import os
import yaml
from collections import defaultdict

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import pandas as pd

from src.modules.skills_dto import SkillDto
from src.modules.model_config import ModelConfig
from src.utils.utils import convert_to_df_description, convert_to_df_names
from src.services import translate_apply_sync
from src.modules.data_reader import DataReader

from pydantic import BaseModel
import json


router = APIRouter()

@router.post("/translate/")
async def translate(file: UploadFile = File(...), data: str = Form(...)):
    try:
        with open('params.yaml', 'r') as f:
            params = yaml.safe_load(f)
        num_processes = params['parallel_processing']['num_processes']

        with open('llm_config.yaml', 'r') as f:
            llm_config = yaml.safe_load(f)
        api_key = llm_config['openai']['api_key']
        model_config = ModelConfig(openai_api_key=api_key, llm_model_name="gpt-3.5-turbo", temperature=0.0)


        file_content = await file.read()
        file_stream = BytesIO(file_content)
        data_dict = json.loads(data)
        sheet_column_pairs = data_dict["sheet_column_pairs"]
        selected_languages = data_dict["selected_languages"]

        if sheet_column_pairs is None:
            raise HTTPException(status_code=400, detail="sheet_column_pairs not provided")

        df_sheet = defaultdict(list)
        output_dir = "translated_files"
        os.makedirs(output_dir, exist_ok=True)

        for pair in sheet_column_pairs:
            sheet = pair.get("sheet")
            column = pair.get("column")
            df = DataReader().read_excel(file_stream, sheet_name=sheet)

            if 'name' in column:
                skills_dtos = [SkillDto(name=row[column], index=index) for index, row in df.iterrows()]
            else:
                skills_dtos = [SkillDto(description=row[column], index=index) for index, row in df.iterrows()]
            print('translating')
            sheet_results = translate_apply_sync(num_processes, model_config, skills_dtos, selected_languages)
            if 'name' in column:
                updated_df = convert_to_df_names(df, sheet_results, selected_languages)
            else:
                updated_df = convert_to_df_description(df, sheet_results, selected_languages)
            print('translated')
            df_sheet[sheet].append(updated_df)
            # updated_df.to_excel(f'translated_descriptions_{sheet}_{column}.xlsx', index=False)

        final_output_files = []
        for sheet, dfs in df_sheet.items():
            original_df = DataReader().read_excel(file_stream, sheet_name=sheet)
            for updated_df in dfs:
                original_df.update(updated_df)
            final_output_path = os.path.join(output_dir, f'translated_descriptions_{sheet}.xlsx')
            original_df.to_excel(final_output_path, index=False)
            final_output_files.append(final_output_path)

        return {"status": "success", "file_path": final_output_files[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    file_location = os.path.join("translated_files", file_path)
    if not os.path.isfile(file_location):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_location)
