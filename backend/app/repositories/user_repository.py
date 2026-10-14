from typing import Optional
from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import IUserRepository

class UserRepository(BaseRepository, IUserRepository):
    def create_user(self, email: str, password_hash: str) -> User:
        db_user = User(email=email, password_hash=password_hash)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def user_exists(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None

