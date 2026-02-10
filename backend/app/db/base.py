from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def load_all_models():
    try:
        from app.db.models.user import User
        from app.db.models.user_permission import UserPermission
        from app.db.models.candidate import Candidate
        from app.db.models.interviewer import Interviewer
        from app.db.models.interview import Interview
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to load database models: {str(e)}") from e
