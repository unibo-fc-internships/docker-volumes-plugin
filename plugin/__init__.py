import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

if not os.environ.get('PLUGIN_NAME'):
    raise ValueError('PLUGIN_NAME is not set in .env file')
if not os.environ.get('PLUGIN_NAME_SHORT'):
    raise ValueError('PLUGIN_NAME_SHORT is not set in .env file')
