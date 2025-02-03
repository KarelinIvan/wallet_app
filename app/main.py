from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import OperationRequest

app = FastAPI()


@app.post("/api/v1/wallets/{wallet_id}/operation")
async def perform_operation(wallet_id: str, request: OperationRequest, db: Session = Depends(get_db)):
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if request.operation_type == "DEPOSIT":
        wallet.balance += request.amount
    elif request.operation_type == "WITHDRAW":
        if wallet.balance < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        wallet.balance -= request.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid operation type")

    crud.update_wallet(db, wallet)
    return {"message": f"{request.operation_type} successful"}


@app.get("/api/v1/wallets/{wallet_id}")
async def get_balance(wallet_id: str, db: Session = Depends(get_db)):
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"balance": wallet.balance}
