from pydantic import BaseModel, Field
from typing import Optional

class SkillDto(BaseModel):
    index: int = Field(description='Talent/Skill')
    name: Optional[str] = Field(default=None, description='skill name')
    type: Optional[str] = Field(default=None, description='Talent/Skill')
    batch: Optional[str] = Field(default=None, description='Batch')
    competency_id: Optional[str] = Field(default=None, description='Competency ID')
    level_id: Optional[str] = Field(default=None, description='Level ID')
    description: Optional[str] = Field(default=None, description='English description')
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
