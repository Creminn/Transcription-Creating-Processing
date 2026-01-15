"""
Processing Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProcessRequest(BaseModel):
    transcription_ids: List[int] = Field(..., description="IDs of transcriptions to process")
    prompt_type: str = Field(..., description="Type of prompt to use")
    llm_model: str = Field(..., description="LLM model to use")
    persona_id: Optional[int] = Field(None, description="Optional persona ID for personalization")
    template_id: Optional[int] = Field(None, description="Optional template ID")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt text if prompt_type is 'custom'")


class ProcessResponse(BaseModel):
    id: int
    prompt_type: str
    transcription_ids: List[int]
    persona_id: Optional[int] = None
    template_id: Optional[int] = None
    llm_model: str
    output_content: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PromptType(BaseModel):
    id: str
    name: str
    description: str


class PromptTypeResponse(BaseModel):
    prompts: List[PromptType]
