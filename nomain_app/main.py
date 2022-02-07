import json
import asyncio
from datetime import datetime

from flask import Flask, Response
import aiohttp

app = Flask(__name__)
loop = asyncio.get_event_loop()


async def session_get(data, url, session):
    try:
        async with session.get(url, timeout=2) as response:
            if response.status == 200 and response.headers.get('content-type') == 'application/json':
                _data = await response.text()
                _data = json.loads(_data)
                data.extend((sorted(_data, key=lambda el: el['id'])))
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                app.logger.info(f"{now}::ERROR {url} STATUS {response.status}")
    except asyncio.TimeoutError as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app.logger.info(f"{now}::ERROR TIMEOUT {url}", e)
    except Exception as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app.logger.info(f"{now}::ERROR {str(e)} {url}", e)


async def get_data(data, urls):
    #   создаем хранилище для задач
    tasks = list()
    #   создаем клиента
    async with aiohttp.ClientSession() as session:
        for url in urls:
            #   добавляем задачи
            tasks.append(asyncio.create_task(session_get(data, url, session)))

        # запускаем задачи
        await asyncio.gather(*tasks)


urls = {
    'http://main_app:8001/get_data_source1',
    'http://main_app:8001/get_data_source2',
    'http://main_app:8001/get_data_source3',
    'http://main_app:8001/get_data_source4'  # пример теймаута
}


@app.route("/")
def hello_world():
    data = list()
    loop.run_until_complete(get_data(data, urls))

    data = sorted(data, key=lambda el: el['id'])

    return Response(response=json.dumps(data), content_type='application/json')
