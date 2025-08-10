from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models.announcement import Announcement
from datetime import datetime

from infrastructure.database.repo.requests import RequestsRepo

new_Announcement_router = Router()

class NewAnnounceForm(StatesGroup):
    people_needed = State()
    route = State()
    start_date = State()
    end_date = State()
    notes = State()

@ new_Announcement_router.message(F.text=="get")
async def get_announcement(message: Message, repo: RequestsRepo):
    print("Nnnndf")
    s=await repo.announcements.get_announcement(message.from_user.id)
    for row in s:
        print(row.id, row.route)

    print(f"Вот такая вот фигня {s}")
@new_Announcement_router.message(F.text == "/new")
async def cmd_new(message: Message, state: FSMContext):
    await message.answer("Сколько человек требуется?")
    await state.set_state(NewAnnounceForm.people_needed)

@new_Announcement_router.message(NewAnnounceForm.people_needed)
async def process_people(message: Message, state: FSMContext):
    await state.update_data(people_needed=int(message.text))
    await message.answer("Введите маршрут (пример: Хэйхэ - Харбин - Бэйдайхэ)")
    await state.set_state(NewAnnounceForm.route)

@new_Announcement_router.message(NewAnnounceForm.route)
async def process_route(message: Message, state: FSMContext):
    await state.update_data(route=message.text)
    await message.answer("Дата начала поездки (ГГГГ-ММ-ДД)")
    await state.set_state(NewAnnounceForm.start_date)

@new_Announcement_router.message(NewAnnounceForm.start_date)
async def process_start_date(message: Message, state: FSMContext):
    await state.update_data(start_date=datetime.strptime(message.text, "%Y-%m-%d").date())
    await message.answer("Дата окончания поездки (ГГГГ-ММ-ДД)")
    await state.set_state(NewAnnounceForm.end_date)

@new_Announcement_router.message(NewAnnounceForm.end_date)
async def process_end_date(message: Message, state: FSMContext):
    await state.update_data(end_date=datetime.strptime(message.text, "%Y-%m-%d").date())
    await message.answer("Примечания (или '-' если нет)")
    await state.set_state(NewAnnounceForm.notes)

# @new_Announcement_router.message(NewAnnounceForm.notes)
# async def process_notes(message: Message, state: FSMContext, repo.session):
#     data = await state.get_data()
#     announcement = Announcement(
#         user_id=message.from_user.id,
#         username=message.from_user.username,
#         people_needed=data['people_needed'],
#         route=data['route'],
#         start_date=data['start_date'],
#         end_date=data['end_date'],
#         notes=None if message.text == "-" else message.text
#     )
#     session.add(announcement)
#     await session.commit()
#
#     await message.answer("✅ Ваша заявка сохранена!")
#     await state.clear()
