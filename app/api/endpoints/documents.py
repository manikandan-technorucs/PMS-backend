from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services import document_service

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
def create_document(document: DocumentCreate, user_id: Optional[int] = 1, db: Session = Depends(get_db)):
    # user_id = 1 represents currently hardcoded active user simulation
    return document_service.create_document(db=db, document=document, user_id=user_id)

@router.get("/", response_model=List[DocumentResponse])
def read_documents(skip: int = 0, limit: int = 100, project_id: int = None, db: Session = Depends(get_db)):
    return document_service.get_documents(db, skip=skip, limit=limit, project_id=project_id)

@router.get("/{document_id}", response_model=DocumentResponse)
def read_document(document_id: int, db: Session = Depends(get_db)):
    db_document = document_service.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: int, document: DocumentUpdate, db: Session = Depends(get_db)):
    db_document = document_service.update_document(db, document_id=document_id, document_update=document)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    success = document_service.delete_document(db, document_id=document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}
