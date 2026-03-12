from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.automation import AutomationRule, AutomationLog
from app.schemas.automation import AutomationRuleCreate, AutomationRuleUpdate, AutomationRuleResponse, AutomationLogResponse
from datetime import datetime, timezone

router = APIRouter()

@router.post("/", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
def create_automation(automation_in: AutomationRuleCreate, db: Session = Depends(get_db)):
    rule = AutomationRule(**automation_in.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.get("/", response_model=List[AutomationRuleResponse])
def get_automations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rules = db.query(AutomationRule).order_by(AutomationRule.id.desc()).offset(skip).limit(limit).all()
    return rules

@router.get("/{rule_id}", response_model=AutomationRuleResponse)
def get_automation(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Automation Rule not found")
    return rule

@router.put("/{rule_id}", response_model=AutomationRuleResponse)
def update_automation(rule_id: int, automation_in: AutomationRuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Automation Rule not found")
    
    update_data = automation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_automation(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Automation Rule not found")
    db.delete(rule)
    db.commit()
    return None

@router.get("/pending-events", response_model=List[AutomationLogResponse])
def get_pending_events(limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns all PENDING automation events. 
    Power Automate polls this endpoint to find new events to process.
    """
    logs = db.query(AutomationLog).filter(
        AutomationLog.execution_status == "PENDING"
    ).order_by(AutomationLog.triggered_at.asc()).limit(limit).all()
    return logs

@router.put("/logs/{log_id}/complete")
def mark_event_complete(
    log_id: int, 
    success: bool = True, 
    error: str = None,
    db: Session = Depends(get_db)
):
    """
    Called by Power Automate after processing an event (sending email).
    Marks the log entry as SUCCESS or FAILED.
    """
    log_entry = db.query(AutomationLog).filter(AutomationLog.id == log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Automation log not found")
    
    log_entry.execution_status = "SUCCESS" if success else "FAILED"
    log_entry.completed_at = datetime.now(timezone.utc)
    if error:
        log_entry.error_message = error
    
    db.commit()
    return {"message": f"Log {log_id} marked as {log_entry.execution_status}"}

@router.get("/{rule_id}/logs", response_model=List[AutomationLogResponse])
def get_automation_logs(rule_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(AutomationLog).filter(AutomationLog.rule_id == rule_id).order_by(AutomationLog.triggered_at.desc()).offset(skip).limit(limit).all()
    return logs
