"""
Benchmark Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TranscriptionBenchmarkRequest(BaseModel):
    media_id: int = Field(..., description="Media file ID to transcribe")
    model_a: str = Field(..., description="First model (baseline)")
    model_b: str = Field(..., description="Second model (challenger)")

    model_config = {"protected_namespaces": ()}


class LLMBenchmarkRequest(BaseModel):
    transcription_id: int = Field(..., description="Transcription ID to process")
    prompt_type: str = Field(..., description="Prompt type to use")
    model_a: str = Field(..., description="First model (baseline)")
    model_b: str = Field(..., description="Second model (challenger)")

    model_config = {"protected_namespaces": ()}


class BenchmarkResultResponse(BaseModel):
    id: int
    benchmark_type: str
    test_name: str
    input_reference: str
    model_a: str
    model_b: str
    output_a: str
    output_b: str
    score_a: Optional[float] = None
    score_b: Optional[float] = None
    judge_model: str
    judge_reasoning: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class BenchmarkListResponse(BaseModel):
    results: List[BenchmarkResultResponse]
    total: int
