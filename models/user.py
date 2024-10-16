from sqlalchemy.orm import Mapped, mapped_column

from db import db
from models.enums import RoleType


class UserModel(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(40), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(13), server_default="Undefined", default="Undefined")
    role: Mapped[RoleType] = mapped_column(
        db.Enum(RoleType), default=RoleType.complainer.name, nullable=False
    )
    certificate = db.Column(db.String(255))
    iban: Mapped[str] = db.Column(db.String(225), nullable=False, default="BG80BNBG96611020345678", server_default="BG80BNBG96611020345678")
