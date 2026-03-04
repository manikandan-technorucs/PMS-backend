from sqlalchemy.orm import Session, joinedload
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

def get_document(db: Session, document_id: int):
    return db.query(Document).options(
        joinedload(Document.uploaded_by)
    ).filter(Document.id == document_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100, project_id: int = None):
    query = db.query(Document).options(
        joinedload(Document.uploaded_by)
    )
    if project_id is not None:
        query = query.filter(Document.project_id == project_id)
    return query.offset(skip).limit(limit).all()

def create_document(db: Session, document: DocumentCreate, user_id: int = None):
    db_document = Document(
        title=document.title,
        description=document.description,
        file_url=document.file_url,
        file_type=document.file_type,
        file_size=document.file_size,
        project_id=document.project_id,
        uploaded_by_id=user_id # In a real app we derive this from the auth token
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return get_document(db, db_document.id)

def update_document(db: Session, document_id: int, document_update: DocumentUpdate):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        return None
    
    update_data = document_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_document, key, value)
        
    db.commit()
    db.refresh(db_document)
    return get_document(db, db_document.id)

def delete_document(db: Session, document_id: int):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        db.delete(db_document)
        db.commit()
        return True
    return False
