from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.category import Category
from app.models.user import User


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene todas las categorías disponibles"""
    categories = db.query(Category).order_by(Category.name).all()
    return categories
