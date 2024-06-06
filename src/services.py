
from multiprocessing import Pool
import sys
import time
from tqdm import tqdm
from typing import List, Tuple

from langchain_core.runnables import RunnableSequence

from modules.model_config import ModelConfig
from modules.openai_chain import OpenAIchain
from modules.translation_prompt import TextTranslationPrompt

from utils.logger import setup_logger


logger = setup_logger(__name__)

            
def batch_text_translate(chain: RunnableSequence, text: str, language_codes: List[str], retries=3, delay=5) -> List[str]:
    for attempt in range(retries):
        try:
            return chain.batch([{'text': text, 'language': lang_code} for lang_code in language_codes])
        except Exception as e:
            logger.warning(f'Attempt {attempt+1} failed with error: {e}')
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logger.warning(f'Failed after {retries} attempts. Returning None.')
                return None


def translate_description(prompt, model_config: ModelConfig, index_text: Tuple[str,str], language_codes: List[str]) -> Tuple[int, List[str]]:
    """
    Translate the text using the OpenAI model
    """
    # with pool.apply_async I can't pass the chain directly as it is not picklable, so create it in the function which is happening over and over again.
    # We need to consider other ways to handle this, as creating the chain every time is not efficient.
    # using manager to share the chain between processes is not possible as the chain is not picklable.
    try:
        chain = OpenAIchain(prompt, model_config).create_chain()
        result = batch_text_translate(chain, index_text[1], language_codes)
        return (index_text[0], result)
    except Exception as e:
        logger.warning(f"Error translating text: {str(e)}")
        return (index_text[0], ['' for _ in language_codes])


class TranslationService:
    """
    class to handle the translation of skills
    """
    def __init__(self, processes: int, model_config: ModelConfig, text_index_pair: List[Tuple[str, str]], language_codes: List[str]):
        self.model_config = model_config
        self.texts = text_index_pair
        self.language_codes = language_codes
        self.processes = processes
        self.prompt = TextTranslationPrompt().create_prompt()

    def translate_apply_sync(self) -> List[Tuple[int, List[str]]]:
        """
        Translate the skills synchronously using multiprocessing
        """
        logger.info(f"Translating {len(self.texts)} skills with {self.processes} processes.")
        with Pool(self.processes) as pool:
            jobs = [pool.apply_async(translate_description, (self.prompt, self.model_config, index_text, self.language_codes))
                     for index_text in self.texts]
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
