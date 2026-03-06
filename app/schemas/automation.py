from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

# --- EmailTemplate Schemas ---
class EmailTemplateBase(BaseModel):
    name: str = Field(..., max_length=255)
    subject: str = Field(..., max_length=255)
    body_html: str
    body_text: Optional[str] = None
    variables_schema: Optional[List[str]] = None
    is_active: bool = True

class EmailTemplateCreate(EmailTemplateBase):
    tenant_id: Optional[str] = None

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    subject: Optional[str] = Field(None, max_length=255)
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    variables_schema: Optional[List[str]] = None
    is_active: Optional[bool] = None

class EmailTemplateResponse(EmailTemplateBase):
    id: int
    version: int
    tenant_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- AutomationRule Schemas ---
class AutomationRuleBase(BaseModel):
    trigger_event: str = Field(..., max_length=100)
    conditions_json: Optional[Dict[str, Any]] = None
    template_id: int
    is_active: bool = True

class AutomationRuleCreate(AutomationRuleBase):
    tenant_id: Optional[str] = None

class AutomationRuleUpdate(BaseModel):
    trigger_event: Optional[str] = Field(None, max_length=100)
    conditions_json: Optional[Dict[str, Any]] = None
    template_id: Optional[int] = None
    is_active: Optional[bool] = None

class AutomationRuleResponse(AutomationRuleBase):
    id: int
    tenant_id: Optional[str] = None
    template: EmailTemplateResponse
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- AutomationLog Schemas ---
class AutomationLogResponse(BaseModel):
    id: int
    rule_id: int
    execution_status: str
    error_message: Optional[str] = None
    idempotency_key: str
    triggered_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
