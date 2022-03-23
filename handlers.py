import logging

from downloader import downloader
from reply_keyboard import markup, markup_remove
from load_all import dp, api
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiovk.exceptions import VkAPIError
from config import VK_API_VER


class Form(StatesGroup):
    waiting_group_name = State()
    waiting_permission = State()


async def get_group_id(group_name: str):
    group_info = api('groups.getById', group_id=group_name, v=VK_API_VER)
    group_list = await group_info()
    group_id = group_list[0]['id']
    return -group_id


async def get_album_ids(group_id: int):
    album_list_ids = []
    albums_info = api('photos.getAlbums', owner_id=group_id, v=VK_API_VER)
    all_albums_dict = await albums_info()
    all_albums_list = all_albums_dict['items']
    for album in all_albums_list:
        album_list_ids.append(album['id'])
    return album_list_ids


# TODO: make default state(menu)

@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
    user = types.User.get_current().username
    text = f'Привет, {user}!\n' \
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
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['get_albums'])
async def get_group_name(message: types.Message):
    text = f'Введите id или название группы\n' \
           f'Пример: https://vk.com/НАЗВАНИЕ_ГРУППЫ'
    await message.answer(text)
    await Form.waiting_group_name.set()


@dp.message_handler(state=Form.waiting_group_name)
async def get_all_albums(message: types.Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    user_data = await state.get_data()
    try:
        group_id = await get_group_id(user_data['group_name'])
        album_list_id = await get_album_ids(group_id)
        text = f'Всего альбомов: {len(album_list_id)}'
        await message.reply(text)
        await Form.next()
        text = f'Скачать альбомы?'
        await message.answer(text, reply_markup=markup)
    except VkAPIError:
        logging.error('Error %r', VkAPIError)
        text = f'Группа не найдена, проверьте правильность написания имени.'
        await message.reply(text)


@dp.message_handler(lambda message: message.text.lower() == 'да', state=Form.waiting_permission)
async def downloading_albums(message: types.Message, state: FSMContext):
    # TODO: send data to downloader
    # downloader()
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == 'нет', state=Form.waiting_permission)
async def return_to_default_state(message: types.Message, state: FSMContext):
    await state.finish()
