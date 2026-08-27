import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./data.db')
APP_BASE_URL=os.getenv('APP_BASE_URL','http://localhost:8000')
DEMO_TOKEN=os.getenv('DEMO_TOKEN','demo-token')
RATE_LIMIT=int(os.getenv('RATE_LIMIT','5')); RATE_WINDOW_SECONDS=int(os.getenv('RATE_WINDOW_SECONDS','60'))
