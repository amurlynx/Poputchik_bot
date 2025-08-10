from aiogram import Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database.models.announcement import Announcement

import os

publish_router = Router()
CHANNEL_ID = 2570221929 #int(os.getenv("CHANNEL_ID"))

@publish_router.message(commands=["publish"])
async def publish_announcements(message: Message, session: AsyncSession):
    if message.from_user.id not in map(int, os.getenv("ADMIN_IDS").split(",")):
        await message.answer("⛔ У вас нет прав для этой команды.")
        return

    result = await session.execute(select(Announcement))
    announcements = result.scalars().all()

    if not announcements:
        await message.answer("Нет заявок для публикации.")
        return

    text = "📢 Актуальные заявки на поиск попутчиков:\n\n"
    for a in announcements:
        text += (
            f"👥 {a.people_needed} чел.\n"
            f"🛤 {a.route}\n"
            f"📅 {a.start_date} - {a.end_date}\n"
            f"💬 {a.notes or '—'}\n"
            f"✉️ @{a.username}\n\n"
        )

    await message.bot.send_message(CHANNEL_ID, text)
    await message.answer("Список опубликован в канал.")
