
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    llm_model_name: str = Field(default='gpt-3.5-turbo', description='openai model name')
    temperature: float = Field(default=0.0, description='openai model temperature')
    openai_api_key: str = Field(description='openai api key')
