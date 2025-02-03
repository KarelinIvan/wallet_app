from pydantic import BaseModel


class OperationRequest(BaseModel):
    operation_type: str
    amount: int
