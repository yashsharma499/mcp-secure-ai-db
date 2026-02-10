from sqlalchemy import Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    table_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    can_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    can_write: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allowed_columns: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    user = relationship("User", lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "table_name", name="uq_user_permissions_user_table"),
    )

    def __repr__(self) -> str:
        return f"<UserPermission user_id={self.user_id} table={self.table_name} read={self.can_read} write={self.can_write}>"
