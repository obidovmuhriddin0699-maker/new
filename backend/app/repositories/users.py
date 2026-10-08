from sqlalchemy import select

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(self._select().where(User.email == email.lower()))

    def get_by_telegram_id(self, telegram_user_id: int) -> User | None:
        return self.session.scalar(self._select().where(User.telegram_user_id == telegram_user_id))

    def get_active(self, user_id: int) -> User | None:
        return self.session.scalar(
            self._select().where(User.id == user_id, User.is_active.is_(True))
        )

    def exists_any(self) -> bool:
        return self.session.scalar(select(User.id).limit(1)) is not None
