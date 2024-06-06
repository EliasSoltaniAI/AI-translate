"""
A module to handle the OpenAI model
"""


from langchain_openai import ChatOpenAI

from modules.model_config import ModelConfig
from utils.logger import setup_logger

logger = setup_logger(__name__)

class OpenAImodel:
    def __init__(self, model_config: ModelConfig):
        self._model = ChatOpenAI(temperature=model_config.temperature, openai_api_key=model_config.openai_api_key, model=model_config.llm_model_name)

    def get_model(self):
        return self._model