import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db_session
from app.db.models.user import User
from app.db.models.user_permission import UserPermission
from app.db.models.candidate import Candidate
from app.db.models.interviewer import Interviewer
from app.db.models.interview import Interview
from app.core.security import hash_password


def seed():
    try:
        with get_db_session() as db:

            now = datetime.now(timezone.utc)

            db.query(Interview).delete()
            db.query(UserPermission).delete()
            db.query(Candidate).delete()
            db.query(Interviewer).delete()
            db.query(User).delete()
            db.flush()

            admin = User(
                email="admin@example.com",
                password_hash=hash_password("Admin@1234"),
                role="admin",
                created_at=now
            )

            user = User(
                email="user@example.com",
                password_hash=hash_password("User@1234"),
                role="user",
                created_at=now
            )

            db.add_all([admin, user])
            db.flush()

            permissions = [
                UserPermission(
                    user_id=user.id,
                    table_name="candidates",
                    can_read=True,
                    can_write=False,
                    allowed_columns=["id", "full_name", "email", "city"]
                ),
                UserPermission(
                    user_id=user.id,
                    table_name="interviews",
                    can_read=True,
                    can_write=False,
                    allowed_columns=["id", "candidate_id", "interviewer_id", "scheduled_at", "status"]
                ),
                UserPermission(
                    user_id=admin.id,
                    table_name="candidates",
                    can_read=True,
                    can_write=True,
                    allowed_columns=None
                ),
                UserPermission(
                    user_id=admin.id,
                    table_name="interviewers",
                    can_read=True,
                    can_write=True,
                    allowed_columns=None
                ),
                UserPermission(
                    user_id=admin.id,
                    table_name="interviews",
                    can_read=True,
                    can_write=True,
                    allowed_columns=None
                )
            ]

            db.add_all(permissions)

            cities = ["Delhi", "Noida", "Gurgaon", "Bangalore", "Pune"]

            candidates = []
            for i in range(1, 21):
                candidates.append(
                    Candidate(
                        full_name=f"Candidate {i}",
                        email=f"candidate{i}@example.com",
                        phone=f"90000000{i:02d}",
                        city=random.choice(cities),
                        created_at=now
                    )
                )

            interviewers = []
            for i in range(1, 6):
                interviewers.append(
                    Interviewer(
                        full_name=f"Interviewer {i}",
                        email=f"interviewer{i}@example.com",
                        department=random.choice(["Engineering", "HR", "Product"]),
                        created_at=now
                    )
                )

            db.add_all(candidates)
            db.add_all(interviewers)
            db.flush()

            interviews = []

            for _ in range(30):
                interviews.append(
                    Interview(
                        candidate_id=random.choice(candidates).id,
                        interviewer_id=random.choice(interviewers).id,
                        scheduled_at=now + timedelta(days=random.randint(-10, 10)),
                        status=random.choice(["scheduled", "completed", "cancelled"]),
                        created_at=now
                    )
                )

            db.add_all(interviews)

    except SQLAlchemyError as e:
        raise RuntimeError(f"Database error during seeding: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"Seeding failed: {str(e)}") from e


if __name__ == "__main__":
    seed()
