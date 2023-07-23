from pydantic import BaseModel
from typing import Any


class ResponseMessage(BaseModel):
    status: str
    data: Any
    message: str
