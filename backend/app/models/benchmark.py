"""
Benchmark Result Model - Stores model comparison benchmark results
"""
from sqlalchemy import Column, Integer, String, Text, Float, JSON, Enum as SQLEnum
from app.database import Base
from app.models.base import TimestampMixin
import enum


class BenchmarkType(str, enum.Enum):
    TRANSCRIPTION = "transcription"
    LLM_PROCESSING = "llm_processing"


class BenchmarkResult(Base, TimestampMixin):
    """Benchmark result model"""
    __tablename__ = "benchmark_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    benchmark_type = Column(SQLEnum(BenchmarkType), nullable=False)
    test_name = Column(String(255), nullable=False)
    input_reference = Column(String(255), nullable=False)  # media_id or transcription_id reference
    model_a = Column(String(100), nullable=False)
    model_b = Column(String(100), nullable=False)
    output_a = Column(Text, nullable=False)
    output_b = Column(Text, nullable=False)
    score_a = Column(Float, nullable=True)
    score_b = Column(Float, nullable=True)
    judge_model = Column(String(100), nullable=False)
    judge_reasoning = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)  # Detailed scores: accuracy, coherence, completeness, style
    
    def __repr__(self):
        return f"<BenchmarkResult(id={self.id}, type='{self.benchmark_type}', models='{self.model_a}' vs '{self.model_b}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "benchmark_type": self.benchmark_type.value,
            "test_name": self.test_name,
            "input_reference": self.input_reference,
            "model_a": self.model_a,
            "model_b": self.model_b,
            "output_a": self.output_a,
            "output_b": self.output_b,
            "score_a": self.score_a,
            "score_b": self.score_b,
            "judge_model": self.judge_model,
            "judge_reasoning": self.judge_reasoning,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
