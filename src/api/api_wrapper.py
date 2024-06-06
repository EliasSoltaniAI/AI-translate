
"""
Contains the main `FastAPI_Wrapper` class, which wraps `FastAPI`.
"""

from collections import defaultdict
from io import BytesIO
import json
from multiprocessing import Pool
import os
import psutil
import time
import threading

from fastapi import FastAPI
from fastapi import File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import yaml

from modules.model_config import ModelConfig
from modules.data_reader import DataReader
from services import TranslationService
from utils.utils import convert_to_df

from utils.logger import setup_logger


logger = setup_logger(__name__)

CORS_ALLOW_ORIGINS=['http://localhost', 'http://localhost:5000', 'http://localhost:8765', 'http://127.0.0.1:5000']

class FastAPI_Wrapper(FastAPI):

    def __init__(self):
        """
        Initializes a FastAPI instance to run translation.
        """
        print('Initializing FastAPI_Wrapper...')
        
        super().__init__()

        origins = CORS_ALLOW_ORIGINS

        self.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add shutdown event (would only be of any use in a multi-process, not multi-thread situation)
        @self.get("/shutdown")
        async def shutdown():

            def suicide():
                time.sleep(1)
                pool.terminate()
                pool.join()
                myself = psutil.Process(os.getpid())
                myself.kill()

            threading.Thread(target=suicide, daemon=True).start()
            logger.info(f'>>> Successfully killed API <<<')
            return {"success": True}  

        @self.post("/translate")
        async def translate(file: UploadFile = File(...), data: str = Form(...)):
            try:
                file_content = await file.read()
                with open('params.yaml', 'r') as f:
                    params = yaml.safe_load(f)
                num_processes = params['parallel_processing']['num_processes']

                with open('llm_config.yaml', 'r') as f:
                    llm_config = yaml.safe_load(f)
                api_key = llm_config['openai']['api_key']
                model_config = ModelConfig(openai_api_key=api_key, 
                                        llm_model_name=params["model"]["model_name"],
                                        temperature=params["model"]["temperature"])

                file_stream = BytesIO(file_content)
                data_dict = json.loads(data)
                sheet_column_pairs = data_dict["sheet_column_pairs"]
                selected_languages = data_dict["selected_languages"]

                if sheet_column_pairs is None:
                    raise HTTPException(status_code=400, detail="sheet_column_pairs not provided")

                df_sheet = defaultdict(list)
                output_dir = "translated_files"
                os.makedirs(output_dir, exist_ok=True)

                global pool
                pool = Pool(num_processes)

                def translate_runner():
                    for pair in sheet_column_pairs:
                        sheet = pair.get("sheet")
                        columns = pair.get("columns")
                        df = DataReader().read_excel(file_stream, sheet_name=sheet)
                        for column in columns:
                            text_index_pairs = list(zip(df.index.tolist(), df[column].tolist()))

                            logger.info(f'translating sheet {sheet} column {column}...')
                            sheet_results = TranslationService(num_processes, model_config, text_index_pairs, selected_languages).translate_apply_sync(pool)

                            updated_df = convert_to_df(df, sheet_results, selected_languages, ('name' if 'name' in column else 'description'))

                            logger.info(f'translated sheet {sheet} column {column}')
                            df_sheet[sheet].append(updated_df)
                    
                    pool.close()
                    pool.join()
                    # Combine all the translated DataFrames and save to a single Excel file
                    final_output_path = os.path.join(output_dir, f'translated_combined.xlsx')
                    with pd.ExcelWriter(final_output_path) as writer:
                        for sheet_name, dfs in df_sheet.items():
                            logger.info(f"Processing sheet: {sheet_name}")
                            # Read the original DataFrame from the file stream once
                            file_stream.seek(0)  # Reset the file stream pointer to the beginning
                            original_df = DataReader().read_excel(file_stream, sheet_name=sheet_name)
                            for updated_df in dfs:
                                original_df.update(updated_df)            
                            original_df.to_excel(writer, index=False, sheet_name=sheet_name)

                    return {"status": "success", "file_path": final_output_path}
                
                threading.Thread(target=translate_runner, daemon=True).start()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

