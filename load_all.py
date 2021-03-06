import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiovk import TokenSession
from aiovk.api import LazyAPI

from config import TG_TOKEN, VK_TOKEN


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=TG_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
session = TokenSession(access_token=VK_TOKEN)
api = LazyAPI(session)
