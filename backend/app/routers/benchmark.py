"""
Benchmark API Router - Handles model benchmarking
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db
from app.models.benchmark import BenchmarkResult, BenchmarkType
from app.models.media import Media
from app.models.transcription import Transcription
from app.schemas.benchmark import (
    TranscriptionBenchmarkRequest, LLMBenchmarkRequest,
    BenchmarkResultResponse, BenchmarkListResponse
)
from app.services.benchmark_service import run_transcription_benchmark, run_llm_benchmark

router = APIRouter()


@router.get("/results", response_model=BenchmarkListResponse)
async def list_benchmark_results(
    benchmark_type: Optional[str] = Query(None, description="Filter by type (transcription, llm_processing)"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all benchmark results"""
    query = select(BenchmarkResult)
    
    if benchmark_type:
        try:
            bt = BenchmarkType(benchmark_type)
            query = query.where(BenchmarkResult.benchmark_type == bt)
        except ValueError:
            pass
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(BenchmarkResult.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    results = result.scalars().all()
    
    return BenchmarkListResponse(
        results=[BenchmarkResultResponse.model_validate(r) for r in results],
        total=total
    )


@router.get("/results/{result_id}", response_model=BenchmarkResultResponse)
async def get_benchmark_result(
    result_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific benchmark result"""
    result = await db.execute(
        select(BenchmarkResult).where(BenchmarkResult.id == result_id)
    )
    benchmark = result.scalar_one_or_none()
    
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark result not found")
    
    return BenchmarkResultResponse.model_validate(benchmark)


@router.post("/transcription", response_model=BenchmarkResultResponse)
async def run_transcription_benchmark_api(
    request: TranscriptionBenchmarkRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run a transcription model benchmark"""
    # Get media file
    result = await db.execute(
        select(Media).where(Media.id == request.media_id)
    )
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media file not found")
    
    # Run benchmark
    success, results, error = await run_transcription_benchmark(
        media.filepath,
        request.model_a,
        request.model_b,
        judge_model='gemini-pro'
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error or "Benchmark failed")
    
    # Save result
    benchmark = BenchmarkResult(
        benchmark_type=BenchmarkType.TRANSCRIPTION,
        test_name=f"Transcription: {media.original_filename}",
        input_reference=f"media:{media.id}",
        model_a=request.model_a,
        model_b=request.model_b,
        output_a=results['output_a'],
        output_b=results['output_b'],
        score_a=results['score_a'],
        score_b=results['score_b'],
        judge_model='gemini-pro',
        judge_reasoning=results['judge_reasoning']
    )
    
    db.add(benchmark)
    await db.commit()
    await db.refresh(benchmark)
    
    return BenchmarkResultResponse.model_validate(benchmark)


@router.post("/llm", response_model=BenchmarkResultResponse)
async def run_llm_benchmark_api(
    request: LLMBenchmarkRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run an LLM processing benchmark"""
    # Get transcription
    result = await db.execute(
        select(Transcription).where(Transcription.id == request.transcription_id)
    )
    transcription = result.scalar_one_or_none()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    # Run benchmark
    success, results, error = await run_llm_benchmark(
        transcription.content,
        request.prompt_type,
        request.model_a,
        request.model_b,
        judge_model='gemini-pro'
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error or "Benchmark failed")
    
    # Save result
    benchmark = BenchmarkResult(
        benchmark_type=BenchmarkType.LLM_PROCESSING,
        test_name=f"LLM ({request.prompt_type}): {transcription.title}",
        input_reference=f"transcription:{transcription.id}",
        model_a=request.model_a,
        model_b=request.model_b,
        output_a=results['output_a'],
        output_b=results['output_b'],
        score_a=results['score_a'],
        score_b=results['score_b'],
        judge_model='gemini-pro',
        judge_reasoning=results['judge_reasoning']
    )
    
    db.add(benchmark)
    await db.commit()
    await db.refresh(benchmark)
    
    return BenchmarkResultResponse.model_validate(benchmark)


@router.delete("/results/{result_id}")
async def delete_benchmark_result(
    result_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a benchmark result"""
    result = await db.execute(
        select(BenchmarkResult).where(BenchmarkResult.id == result_id)
    )
    benchmark = result.scalar_one_or_none()
    
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark result not found")
    
    await db.delete(benchmark)
    await db.commit()
    
    return {"message": "Benchmark result deleted successfully"}


@router.get("/models/transcription")
async def get_transcription_models():
    """Get available transcription models for benchmarking"""
    from app.services.transcription.transcription_service import get_available_models
    return {"models": get_available_models()}


@router.get("/models/llm")
async def get_llm_models():
    """Get available LLM models for benchmarking"""
    from app.services.llm.llm_service import get_available_models
    return {"models": get_available_models()}
