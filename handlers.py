import logging

from downloader import downloader
from reply_keyboard import markup, markup_remove
from load_all import dp
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiovk.exceptions import VkAPIError
from vk_func import get_group_id, get_photos, get_album_ids, complete_albums


class Form(StatesGroup):
    waiting_group_name = State()
    waiting_permission = State()
    saving_album_dict = State()


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
        await state.update_data(group_id=group_id)
        album_list_id = await get_album_ids(group_id)
        await state.update_data(album_list_id=album_list_id)
        text = f'Всего альбомов: {len(album_list_id)}'
        await message.reply(text)

        current_state = await state.get_state()
        logging.info('Current state %r', current_state)

        await Form.next()
        text = f'Скачать альбомы?'
        await message.answer(text, reply_markup=markup)
    except VkAPIError:
        logging.error('Error %r', VkAPIError)
        text = f'Группа не найдена, проверьте правильность написания имени.'
        await message.reply(text)


@dp.message_handler(lambda message: message.text.lower() == 'да', state=Form.waiting_permission)
async def downloading_albums(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    logging.info('Current state %r', current_state)

    user_data = await state.get_data()
    group_id = user_data['group_id']
    album_list_id = user_data['album_list_id']
    all_album_dict = await get_photos(group_id,  album_list_id)
    await state.update_data(all_album_dict=all_album_dict)
    all_albums = await complete_albums(all_album_dict)
    text = f'Скачивание началось.\n' \
           f'Проверьте папку "Загрузки".'
    await message.answer(text, reply_markup=markup_remove)
    downloader(all_albums)
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == 'нет', state=Form.waiting_permission)
async def return_to_default_state(message: types.Message, state: FSMContext):
    await state.finish()

    current_state = await state.get_state()
    logging.info('Current state %r', current_state)
