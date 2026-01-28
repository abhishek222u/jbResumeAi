import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    API_KEY: str = os.getenv("HF_API_KEY")
    
    Project_Name: str = "Mock_Interview_Platform"
    API_VERSION: str = "v1"


settings = Settings()    