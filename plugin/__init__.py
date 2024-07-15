import os

from dotenv import load_dotenv

load_dotenv('../.env')

if not os.environ.get('PLUGIN_NAME'):
    raise ValueError('PLUGIN_NAME is not set in .env file')