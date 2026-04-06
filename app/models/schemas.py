from pydantic import BaseModel
from typing import Dict

class ToolRequest(BaseModel):
    name: str
    arguments: Dict