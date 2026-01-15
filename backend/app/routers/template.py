"""
Template API Router - Handles email template CRUD operations
"""
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.database import get_db
from app.models.template import EmailTemplate, TemplateCategory
from app.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse
)

router = APIRouter()


def extract_placeholders(content: str) -> List[str]:
    """Extract placeholder names from template content"""
    pattern = r'\{\{(\w+)\}\}'
    return list(set(re.findall(pattern, content)))


AVAILABLE_PLACEHOLDERS = [
    {'key': '{{meeting_date}}', 'description': 'Date of the meeting'},
    {'key': '{{attendees}}', 'description': 'List of attendees'},
    {'key': '{{summary}}', 'description': 'Generated meeting summary'},
    {'key': '{{action_items}}', 'description': 'List of action items'},
    {'key': '{{next_steps}}', 'description': 'Next steps from the meeting'},
    {'key': '{{decisions}}', 'description': 'Key decisions made'},
    {'key': '{{topics}}', 'description': 'Topics discussed'},
    {'key': '{{owner}}', 'description': 'Meeting owner/organizer'},
    {'key': '{{date}}', 'description': 'Current date'},
]


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Only return active templates"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all email templates"""
    query = select(EmailTemplate)
    
    if category:
        try:
            cat = TemplateCategory(category)
            query = query.where(EmailTemplate.category == cat)
        except ValueError:
            pass
    
    if active_only:
        query = query.where(EmailTemplate.is_active == True)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(EmailTemplate.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return TemplateListResponse(
        templates=[TemplateResponse.model_validate(t) for t in templates],
        total=total
    )


@router.get("/categories")
async def get_categories():
    """Get available template categories"""
    return {
        "categories": [
            {'id': 'meeting_notes', 'name': 'Meeting Notes'},
            {'id': 'follow_up', 'name': 'Follow Up'},
            {'id': 'summary', 'name': 'Summary'},
            {'id': 'training', 'name': 'Training'},
            {'id': 'custom', 'name': 'Custom'},
        ]
    }


@router.get("/placeholders")
async def get_placeholders():
    """Get available placeholders for templates"""
    return {"placeholders": AVAILABLE_PLACEHOLDERS}


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template by ID"""
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse.model_validate(template)


@router.post("", response_model=TemplateResponse)
async def create_template(
    request: TemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new email template"""
    # Extract placeholders from content
    placeholders = extract_placeholders(request.template_content)
    
    # Validate category
    try:
        category = TemplateCategory(request.category)
    except ValueError:
        category = TemplateCategory.CUSTOM
    
    template = EmailTemplate(
        name=request.name,
        category=category,
        template_content=request.template_content,
        placeholders=placeholders
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse.model_validate(template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    request: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a template"""
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update fields
    if request.name is not None:
        template.name = request.name
    
    if request.category is not None:
        try:
            template.category = TemplateCategory(request.category)
        except ValueError:
            template.category = TemplateCategory.CUSTOM
    
    if request.template_content is not None:
        template.template_content = request.template_content
        template.placeholders = extract_placeholders(request.template_content)
    
    if request.is_active is not None:
        template.is_active = request.is_active
    
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse.model_validate(template)


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a template"""
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await db.delete(template)
    await db.commit()
    
    return {"message": "Template deleted successfully"}
