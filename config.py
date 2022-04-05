from environs import Env
from sqlalchemy import create_engine

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
DATABASE = env.str("DATABASE")
# подключение к бд
engine = create_engine(f"sqlite:///{DATABASE}"
                       "?check_same_thread=False")

ADMINS = [477733380]
