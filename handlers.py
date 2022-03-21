import logging

from load_all import dp, api, loop
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config import VK_API_VER


class Form(StatesGroup):
    waiting_group_name = State()


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
    user = types.User.get_current().username
    text = f'Привет,{user}!\n' \
           f'Воспользуйся /get_albums чтобы скачать альбомы.'
    await message.answer(text)


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.')


@dp.message_handler(commands=['get_albums'])
async def get_group_name(message: types.Message):
    text = f'Введите id или название группы\n' \
           f'Пример: https://vk.com/НАЗВАНИЕ_ГРУППЫ'
    await message.answer(text)
    await Form.waiting_group_name.set()


@dp.message_handler(state=Form.waiting_group_name)
async def get_all_albums(message: types.Message, state: FSMContext):
    logging.info('Creating list for albums')
    album_list_ids = []
    await state.update_data(group_name=message.text)
    user_data = await state.get_data()
    logging.info('Getting data')
    group_info = api('groups.getById', group_id=user_data['group_name'], v=VK_API_VER)
    group_id = (await group_info())[0]['id']
    albums_info = api('photos.getAlbums', owner_id=-group_id, v=VK_API_VER)
    all_albums = (await albums_info())['items']
    for album in all_albums:
        album_list_ids.append(album['id'])
    text = f'Всего альбомов: {len(album_list_ids)}'
    await message.reply(text)
