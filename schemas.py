from pydantic import BaseModel
from typing import Optional, Dict, Any

class RunGraphRequest(BaseModel):
    start_node: str
    initial_state: Optional[Dict[str, Any]] = None
    max_steps: int = 1000
