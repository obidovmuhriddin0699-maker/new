from collections.abc import Sequence

from sqlalchemy import select

from app.models import InstagramAccount, OAuthToken
from app.repositories.base import BaseRepository


class InstagramAccountRepository(BaseRepository[InstagramAccount]):
    model = InstagramAccount

    def get_by_ig_user_id(
        self, ig_user_id: str, *, include_deleted: bool = False
    ) -> InstagramAccount | None:
        return self.session.scalar(
            self._select(include_deleted=include_deleted).where(
                InstagramAccount.ig_user_id == ig_user_id
            )
        )

    def list_for_user(self, user_id: int) -> Sequence[InstagramAccount]:
        return self.session.scalars(
            self._select().where(InstagramAccount.user_id == user_id).order_by(InstagramAccount.id)
        ).all()


class OAuthTokenRepository(BaseRepository[OAuthToken]):
    model = OAuthToken

    def get_active_for_account(self, account_id: int) -> OAuthToken | None:
        return self.session.scalar(
            select(OAuthToken)
            .where(OAuthToken.instagram_account_id == account_id, OAuthToken.revoked_at.is_(None))
            .order_by(OAuthToken.id.desc())
            .limit(1)
        )

    def list_active_for_account(self, account_id: int) -> Sequence[OAuthToken]:
        return self.session.scalars(
            select(OAuthToken).where(
                OAuthToken.instagram_account_id == account_id, OAuthToken.revoked_at.is_(None)
            )
        ).all()
