import time
from multiprocessing import Pool
from tqdm import tqdm
from typing import List, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from src.modules.skills_dto import SkillDto
from src.modules.model_config import ModelConfig
import sys


def prompt_to_translate_description():
    prompt = ChatPromptTemplate.from_messages([
        ('system', 'You are an excellent multilingual translator. Translate the description to language: {language}. Use clear, professional and formal language.'),
        ('human', '{description}')
    ])
    return prompt

def prompt_to_translate_skill_name():
    prompt = ChatPromptTemplate.from_messages([
        ('system', """You are an excellent multilingual translator. You are given a skill name and a description for the skill.
          Translate the skill name to language: {language}. Do not translate skill description only skill name. Use clear, professional and formal translation for the skill name."""),
        ('human', 'skill name: {skill_name}, description:{description}')
    ])
    return prompt

def prompt_to_translate_skill_name_only():
    prompt = ChatPromptTemplate.from_messages([
        ('system', """You are an excellent multilingual translator. You are given a skill name.
          Translate the skill name to language: {language}. Use clear, professional and formal translation for the skill name."""),
        ('human', '{skill_name}')
    ])
    return prompt

def create_chain(prompt, model_config: ModelConfig) -> RunnableSequence:
    model = ChatOpenAI(temperature=model_config.temperature, openai_api_key=model_config.openai_api_key, model=model_config.llm_model_name)
    output_parser = StrOutputParser()
    return prompt | model | output_parser

def batch_lang_translate(chain: RunnableSequence, text: str, language_codes: List[str], retries=3, delay=5) -> List[str]:
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
            
def batch_lang_translate_name(chain: RunnableSequence, text: str, language_codes: List[str], retries=3, delay=5) -> List[str]:
    for attempt in range(retries):
        try:
            return chain.batch([{'skill_name': text, 'language': lang_code} for lang_code in language_codes])
        except Exception as e:
            print(f'Attempt {attempt+1} failed with error: {e}')
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f'Failed after {retries} attempts. Returning None.')
                return None

def translate_description(model_config: ModelConfig, skill: SkillDto, language_codes: List[str]) -> Tuple[int, List[str]]:
    try:
        if skill.name:
            prompt = prompt_to_translate_skill_name_only()
            chain = create_chain(prompt, model_config)
            result = batch_lang_translate_name(chain, skill.name, language_codes)
        else:
            prompt = prompt_to_translate_description()
            chain = create_chain(prompt, model_config)
            result = batch_lang_translate(chain, skill.description, language_codes)
        return (skill.index, result)
    except Exception as e:
        return (skill.index, None, str(e))

def translate_apply_sync(processes: int, model_config: ModelConfig, skill_dtos: List[SkillDto], language_codes: List[str]) -> List[Tuple[int, List[str]]]:
    with Pool(processes) as pool:
        jobs = [pool.apply_async(translate_description, (model_config, skill, language_codes)) for skill in skill_dtos]
        try:
            results = [res.get() for res in tqdm(jobs)]
        except KeyboardInterrupt:
            print("Interrupted by user. Terminating processes.")
            pool.terminate()
            pool.join()
            sys.exit(0)
        except Exception as e:
            print(f"Error retrieving results: {e}")
            pool.terminate()
            pool.join()
        finally:
            pool.close()
            pool.join()
    return results
