import os
import base64

from dotenv import load_dotenv


load_dotenv()

TG_TOKEN = base64.b64decode(os.getenv("TG_TOKEN")).decode("utf-8")
VK_TOKEN = base64.b64decode(os.getenv("VK_TOKEN")).decode("utf-8")
VK_API_VER = os.getenv("VK_API_VER")
