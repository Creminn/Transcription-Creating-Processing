"""
Processing API Router - Handles prompt processing with LLMs
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.transcription import Transcription
from app.models.persona import Persona
from app.models.template import EmailTemplate
from app.models.processed_output import ProcessedOutput
from app.schemas.processing import ProcessRequest, ProcessResponse, PromptTypeResponse
from app.services.llm.llm_service import generate, get_available_models as get_llm_models
from app.services.prompt_templates import build_prompt, get_all_prompt_types

router = APIRouter()


@router.get("/prompts", response_model=PromptTypeResponse)
async def get_prompt_types():
    """Get available prompt types"""
    return PromptTypeResponse(prompts=get_all_prompt_types())


@router.get("/models")
async def get_models():
    """Get available LLM models"""
    return {"models": get_llm_models()}


@router.post("", response_model=ProcessResponse)
async def process_transcriptions(
    request: ProcessRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process transcriptions with selected prompt and LLM"""
    if not request.transcription_ids:
        raise HTTPException(status_code=400, detail="No transcription IDs provided")
    
    # Get transcriptions
    result = await db.execute(
        select(Transcription).where(Transcription.id.in_(request.transcription_ids))
    )
    transcriptions = result.scalars().all()
    
    if not transcriptions:
        raise HTTPException(status_code=404, detail="No transcriptions found")
    
    # Combine transcription content
    combined_content = "\n\n---\n\n".join([
        f"# {t.title}\n{t.content}" for t in transcriptions
    ])
    
    # Get persona if specified
    persona_style = None
    if request.persona_id:
        persona_result = await db.execute(
            select(Persona).where(Persona.id == request.persona_id)
        )
        persona = persona_result.scalar_one_or_none()
        if persona:
            # Build persona style instructions
            persona_style = f"""Write in the style of {persona.name}:
{persona.style_description}

Sample writing examples:
{chr(10).join([f'- {email[:200]}...' for email in (persona.sample_emails or [])[:3]])}
"""
    
    # Get template if specified
    template_content = None
    if request.template_id:
        template_result = await db.execute(
            select(EmailTemplate).where(EmailTemplate.id == request.template_id)
        )
        template = template_result.scalar_one_or_none()
        if template:
            template_content = template.template_content
    
    # Build prompt
    system_prompt, user_prompt = build_prompt(
        request.prompt_type,
        combined_content,
        request.custom_prompt,
        persona_style,
        template_content
    )
    
    # Generate with LLM
    success, output_text, usage, error = await generate(
        user_prompt,
        model=request.llm_model,
        system_prompt=system_prompt
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error or "LLM generation failed")
    
    # Save processed output
    processed = ProcessedOutput(
        prompt_type=request.prompt_type,
        transcription_ids=request.transcription_ids,
        persona_id=request.persona_id,
        template_id=request.template_id,
        llm_model=request.llm_model,
        custom_prompt=request.custom_prompt,
        input_tokens=usage.get('input_tokens') if usage else None,
        output_tokens=usage.get('output_tokens') if usage else None,
        output_content=output_text or ""
    )
    
    db.add(processed)
    await db.commit()
    await db.refresh(processed)
    
    return ProcessResponse.model_validate(processed)


@router.get("/history")
async def get_processing_history(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get processing history"""
    query = select(ProcessedOutput).order_by(ProcessedOutput.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    outputs = result.scalars().all()
    
    return {
        "outputs": [ProcessResponse.model_validate(o) for o in outputs],
        "page": page,
        "limit": limit
    }


@router.get("/{output_id}", response_model=ProcessResponse)
async def get_processed_output(
    output_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific processed output"""
    result = await db.execute(
        select(ProcessedOutput).where(ProcessedOutput.id == output_id)
    )
    output = result.scalar_one_or_none()
    
    if not output:
        raise HTTPException(status_code=404, detail="Processed output not found")
    
    return ProcessResponse.model_validate(output)
