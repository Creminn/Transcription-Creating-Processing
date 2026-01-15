"""
Persona API Router - Handles persona CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models.persona import Persona
from app.schemas.persona import (
    PersonaCreate, PersonaUpdate, PersonaResponse, PersonaListResponse
)

router = APIRouter()


@router.get("", response_model=PersonaListResponse)
async def list_personas(
    active_only: bool = Query(True, description="Only return active personas"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all personas"""
    query = select(Persona)
    
    if active_only:
        query = query.where(Persona.is_active == True)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Persona.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    personas = result.scalars().all()
    
    return PersonaListResponse(
        personas=[PersonaResponse.model_validate(p) for p in personas],
        total=total
    )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific persona by ID"""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    return PersonaResponse.model_validate(persona)


@router.post("", response_model=PersonaResponse)
async def create_persona(
    request: PersonaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new persona"""
    # Check for duplicate name
    existing = await db.execute(
        select(Persona).where(Persona.name == request.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Persona with this name already exists")
    
    persona = Persona(
        name=request.name,
        sample_emails=request.sample_emails,
        style_description=request.style_description
    )
    
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    
    return PersonaResponse.model_validate(persona)


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    request: PersonaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a persona"""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Update fields
    if request.name is not None:
        # Check for duplicate name
        existing = await db.execute(
            select(Persona).where(
                Persona.name == request.name,
                Persona.id != persona_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Persona with this name already exists")
        persona.name = request.name
    
    if request.sample_emails is not None:
        persona.sample_emails = request.sample_emails
    
    if request.style_description is not None:
        persona.style_description = request.style_description
    
    if request.is_active is not None:
        persona.is_active = request.is_active
    
    await db.commit()
    await db.refresh(persona)
    
    return PersonaResponse.model_validate(persona)


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a persona"""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    await db.delete(persona)
    await db.commit()
    
    return {"message": "Persona deleted successfully"}


@router.get("/guidance/tips")
async def get_persona_guidance():
    """Get guidance on creating effective personas"""
    return {
        "guidance": {
            "what_is_persona": "A persona captures a person's unique writing style. When applied to generated emails, the AI will mimic their tone, vocabulary, and communication patterns.",
            "best_practices": [
                "Include 3-5 diverse email samples that represent different contexts (formal updates, casual check-ins, etc.)",
                "Choose emails that showcase signature phrases, greetings, and sign-offs",
                "In the style description, note specific traits: 'Uses bullet points, starts with Hi team, ends with Best'",
                "Mention formality level: casual, professional, friendly-professional"
            ],
            "example_style_description": "Zeynep writes in a warm, professional tone. She uses concise sentences and bullet points for clarity. Typically starts emails with 'Hi [name]' and ends with 'Best regards' or just 'Best'. Often includes a friendly closing line like 'Let me know if you have questions!' Uses exclamation marks sparingly but effectively."
        }
    }
