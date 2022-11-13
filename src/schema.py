from typing import AnyStr, Dict, List
from pydantic import BaseModel

class Form(BaseModel):
    name: AnyStr
    description: AnyStr
    fields: List[Dict[AnyStr, AnyStr]]

class FormData(BaseModel):
    form_id: str
    data: Dict[str, str]

class QueryForm(BaseModel):
    query: str

class WebhookData(BaseModel):
    url: str
    form_id: str | None
    query: str | None
