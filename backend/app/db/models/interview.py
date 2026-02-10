from datetime import datetime
from sqlalchemy import Integer, DateTime, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    interviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("interviewers.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_interviews_candidate_interviewer", "candidate_id", "interviewer_id"),
    )

    def __repr__(self) -> str:
        return f"<Interview id={self.id} candidate_id={self.candidate_id} interviewer_id={self.interviewer_id} status={self.status}>"
