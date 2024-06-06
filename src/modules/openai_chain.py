"""
This module is responsible for creating the chain of modules for OpenAI
"""

from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser

from modules.model_config import ModelConfig
from modules.openai_model import OpenAImodel
from utils.logger import setup_logger

logger = setup_logger(__name__)

class OpenAIchain:
    """
    class to create the chain of modules for OpenAI
    """
    def __init__(self,prompt, model_config: ModelConfig):
        self.model_config = model_config
        self.prompt = prompt

    def create_chain(self) -> RunnableSequence:
        """
        create the chain of modules for OpenAI
        """
        try:
            model = OpenAImodel(self.model_config).get_model()
            output_parser = StrOutputParser()
            return self.prompt | model | output_parser
        except Exception as e:
            logger.error(f"Error creating OpenAI chain: {str(e)}")
