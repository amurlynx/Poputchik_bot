from typing import Optional, Dict, Any, Coroutine, Sequence

from aiogram.types import Message
from sqlalchemy import select, Row, RowMapping
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import Announcement, User
from infrastructure.database.repo.base import BaseRepo


class AnnouncementRepo(BaseRepo):
    async def get_announcement(self, user_id: int) -> Sequence[Announcement]:
        result= await self.session.execute(select(Announcement).where(Announcement.user_id == user_id))
        await self.session.commit()
        return result.scalars().all()

    async def edit_announcement(self, data: Announcement):
        pass

    async def delete_announcement(self, announcement_id: int):
        pass

    async def post_announcement(self, data:Dict[str,any]) -> None:

        insert_stmt = (
            insert(Announcement)
            .values(
                user_id=data['user_id'],
                user_name=data['user_name'],
                people_needed=data['people_needed'],
                route=data['route'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                notes=data['notes'],
            )
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()

    async def get_or_create_user(
        self,
        user_id: int,
        full_name: str,
        language: str,
        username: Optional[str] = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """

        insert_stmt = (
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                full_name=full_name,
                language=language,
            )
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_=dict(
                    username=username,
                    full_name=full_name,
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()
