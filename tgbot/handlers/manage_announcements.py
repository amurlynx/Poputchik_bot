from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from infrastructure.database.models.announcement import Announcement
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

manage_Announcement_router = Router()

class EditForm(StatesGroup):
    field = State()
    value = State()

@manage_Announcement_router .message(F.text == "/my")
async def my_announcements(message: Message, session: AsyncSession):
    result = await session.execute(
        select(Announcement).where(Announcement.user_id == message.from_user.id)
    )
    announcements = result.scalars().all()
    if not announcements:
        await message.answer("У вас нет активных заявок.")
        return

    for a in announcements:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit:{a.id}")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del:{a.id}")]
        ])
        await message.answer(
            f"#{a.id}\n👥 {a.people_needed}\n🛤 {a.route}\n📅 {a.start_date} - {a.end_date}\n💬 {a.notes or '—'}",
            reply_markup=kb
        )

@manage_Announcement_router .callback_query(F.data.startswith("del:"))
async def delete_announcement(callback: CallbackQuery, session: AsyncSession):
    ann_id = int(callback.data.split(":")[1])
    await session.execute(
        delete(Announcement).where(
            Announcement.id == ann_id,
            Announcement.user_id == callback.from_user.id
        )
    )
    await session.commit()
    await callback.message.edit_text("✅ Заявка удалена.")

@manage_Announcement_router .callback_query(F.data.startswith("edit:"))
async def choose_field(callback: CallbackQuery, state: FSMContext):
    ann_id = int(callback.data.split(":")[1])
    await state.update_data(ann_id=ann_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Кол-во людей", callback_data="field:people_needed")],
        [InlineKeyboardButton(text="🛤 Маршрут", callback_data="field:route")],
        [InlineKeyboardButton(text="📅 Дата начала", callback_data="field:start_date")],
        [InlineKeyboardButton(text="📅 Дата окончания", callback_data="field:end_date")],
        [InlineKeyboardButton(text="💬 Примечания", callback_data="field:notes")]
    ])
    await callback.message.answer("Что изменить?", reply_markup=kb)

@manage_Announcement_router .callback_query(F.data.startswith("field:"))
async def start_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await callback.message.answer(f"Введите новое значение для {field}:")
    await state.set_state(EditForm.value)

@manage_Announcement_router .message(EditForm.value)
async def save_edit(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    ann_id = data["ann_id"]
    field = data["field"]
    value = message.text

    if field in ["start_date", "end_date"]:
        value = datetime.strptime(value, "%Y-%m-%d").date()
    elif field == "people_needed":
        value = int(value)

    announcement = await session.get(Announcement, ann_id)
    if announcement and announcement.user_id == message.from_user.id:
        setattr(announcement, field, value)
        await session.commit()
        await message.answer("✅ Изменения сохранены.")
    else:
        await message.answer("⛔ Заявка не найдена.")
    await state.clear()
