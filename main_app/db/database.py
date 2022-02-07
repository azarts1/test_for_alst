import os
import socket
import time

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = url if (url := os.getenv("DB_URL")) else ''

#   ждем пока поднимется постргерс в контейнере, depends_on не отрабатывает нормально
#   предполагаю, если самому писать DockerFile для постгреса можно избежать такой проблемы
if (port := os.getenv("POSTGRES_PORT")) and (host := os.getenv("POSTGRES_HOST")):
    port = int(port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((host, port))
            s.close()
            break
        except socket.error as ex:
            time.sleep(0.1)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        async with session.begin():
            yield session

