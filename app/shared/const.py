import os

from dotenv import load_dotenv

load_dotenv()

url = os.getenv("url")
bucket = os.getenv("bucket")

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

cdn = os.getenv("cdn")
