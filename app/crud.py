from sqlalchemy.orm import Session

from app.models import Wallet


def get_wallet(db: Session, wallet_id: str):
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()


def update_wallet(db: Session, wallet: Wallet):
    db.add(wallet)
    db.commit()
    return wallet
