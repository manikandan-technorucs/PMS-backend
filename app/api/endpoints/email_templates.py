from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.automation import EmailTemplate
from app.schemas.automation import EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse

router = APIRouter()

@router.post("/", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(template_in: EmailTemplateCreate, db: Session = Depends(get_db)):
    template = EmailTemplate(**template_in.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/", response_model=List[EmailTemplateResponse])
def get_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = db.query(EmailTemplate).order_by(EmailTemplate.id.desc()).offset(skip).limit(limit).all()
    return templates

@router.get("/{template_id}", response_model=EmailTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email Template not found")
    return template

@router.put("/{template_id}", response_model=EmailTemplateResponse)
def update_template(template_id: int, template_in: EmailTemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email Template not found")
    
    update_data = template_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    template.version += 1 # Auto increment version
    
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email Template not found")
    
    # Soft delete
    template.is_active = False
    db.commit()
    return None
