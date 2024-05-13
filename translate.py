
import multiprocessing
from pydantic import BaseModel, Field
import time
from tqdm import tqdm
from typing import List, Optional, Tuple
import yaml

from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
import pandas as pd


class SkillDto(BaseModel):
    index: int = Field(description='Talent/Skill')
    type: Optional[str] = Field(default=None, description='Talent/Skill')
    batch: Optional[str] = Field(default=None, description='Batch')
    competency_id: Optional[str] = Field(default=None, description='Competency ID')
    level_id: Optional[str] = Field(default=None, description='Level ID')
    description: str = Field(description='English description')
    zh_CN_description: Optional[str] = Field(default=None, description='Chinese Simplified description')
    it_description: Optional[str] = Field(default=None, description='Italian description')
    fr_description: Optional[str] = Field(default=None, description='French description')
    de_description: Optional[str] = Field(default=None, description='German description')
    ja_description: Optional[str] = Field(default=None, description='Japanese description')
    ko_description: Optional[str] = Field(default=None, description='Korean description')
    pt_BR_description: Optional[str] = Field(default=None, description='Portuguese (Brazil) description')
    es_419_description: Optional[str] = Field(default=None, description='Spanish Latam description')
    tr_description: Optional[str] = Field(default=None, description='Turkish description')
    es_description: Optional[str] = Field(default=None, description='Spanish (EU) description')
    nl_description: Optional[str] = Field(default=None, description='Dutch description')
    ru_description: Optional[str] = Field(default=None, description='Russian description')
    pl_description: Optional[str] = Field(default=None, description='Polish description')


class ModelConfig(BaseModel):
    llm_model_name: str = Field(default='gpt-3.5-turbo', description='openai model name')
    temperature: float = Field(default=0.0, description='openai model temperature')
    openai_api_key: str = Field(description='openai api key')


def get_dataframe(file_name: str) -> pd.DataFrame:
    df = pd.read_excel(file_name, sheet_name=0, header=0)
    for col in df.columns:
        df[col] = df[col].astype(str)
    return df


def get_languages_from_df_column_names(df: pd.DataFrame) -> List[str]:
    return [col.replace(' description', '') for col in df.columns if 'description' in col and col != 'description']


def batch_lang_translate(chain: RunnableSequence, text: str, language_codes: List[str],
                          retries=3, delay=2) -> List[str]:
    """Translate a single description to multiple languages."""
    for attempt in range(retries):
        try:
            return chain.batch([{'description': text, 'language': lang_code} for lang_code in language_codes])
        except Exception as e:
            print(f'Attempt {attempt+1} failed with error: {e}')
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f'Failed after {retries} attempts. Returning None.')
                return None
            
def create_chain(model_config: ModelConfig) -> RunnableSequence:
    prompt = ChatPromptTemplate.from_messages([
        ('system', 'You are an excellent multilingual translator. Translate the description to language: {language}. Use clear, professional and formal language.'),
        ('human', '{description}')
    ])
    model = ChatOpenAI(temperature=model_config.temperature, openai_api_key=model_config.openai_api_key,
                        model=model_config.llm_model_name)
    output_parser = StrOutputParser()
    return prompt | model | output_parser


def translate_description(model_config: ModelConfig, skill: SkillDto, language_codes: List[str]) -> Tuple[int, List[str]]:
    """Translate a single description to multiple languages."""
    chain= create_chain(model_config)  # chain is not picklable, so we need to create it in the worker
    try:
        result = batch_lang_translate(chain, skill.description, language_codes)
        return (skill.index, result)
    except Exception as e:
        return (skill.competency_id, None, str(e))
    
def update_df(df: pd.DataFrame, results: List[Tuple[int, List[str]]], language_codes: List[str]) -> pd.DataFrame:
    update_data = {'index': []}
    for code in language_codes:
        update_data[f'{code} description'] = []

    for index, translations in results:
        update_data['index'].append(index)
        for lang_index, translation in enumerate(translations):
            lang_code = language_codes[lang_index]
            update_data[f'{lang_code} description'].append(translation)

    temp_df = pd.DataFrame(update_data).set_index('index')

    df.update(temp_df)
    return df
    

def translate_apply_sync(processes:int, skill_dtos: List[SkillDto], language_codes: List[str]) -> List[Tuple[int, List[str]]]:
    with multiprocessing.Pool(processes) as pool:
        jobs = [pool.apply_async(translate_description, 
                                    ((model_config, skill, language_codes))) for skill in skill_dtos]
        try:
            results = [res.get() for res in tqdm(jobs)]
        except Exception as e:
            print(f"Error retrieving results: {e}")
    return results


if __name__ == '__main__':
    PROCESSES = 6
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)

    file_name = params['competency-data']['data_path']
    df = get_dataframe(file_name)

    language_codes = get_languages_from_df_column_names(df)

    with open('llm_config.yaml', 'r') as f:
        llm_config = yaml.safe_load(f)
    api_key = llm_config['openai']['api_key']

    model_config = ModelConfig(openai_api_key=api_key, llm_model_name=params['model']['model_name'],
                                temperature=params['model']['temperature'])

    skills_dtos = [
        SkillDto(description=row['description'],
                 index=index) for index, row in df.iterrows()
    ]

    results = translate_apply_sync(PROCESSES, skills_dtos, language_codes)
    df = update_df(df, results, language_codes)
    df.to_excel('translated_descriptions.xlsx', index=False)
