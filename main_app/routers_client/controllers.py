import asyncio
import json

from fastapi import status, Request, APIRouter
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

router_client = APIRouter(tags=["client"])

templates = Jinja2Templates(directory="templates")


@router_client.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
    })


@router_client.get("/users", response_class=HTMLResponse)
async def users(request: Request):
    return templates.TemplateResponse("users.html", {
        "request": request,
    })


#   тут апишки для 2 пункта, решил не делать файлы, а просто генерить результат по факту вызова
@router_client.get("/get_data_source1", response_class=HTMLResponse)
async def get_data_source1():
    result = list()
    for i in range(1, 11):
        result.append(dict(id=i, name=f'Test {i}'))
    for i in range(31, 41):
        result.append(dict(id=i, name=f'Test {i}'))

    return Response(
        headers={"Content-Type": "application/json"},
        status_code=status.HTTP_200_OK,
        content=json.dumps(result)
    )


@router_client.get("/get_data_source2", response_class=HTMLResponse)
async def get_data_source2():
    result = list()
    for i in range(11, 21):
        result.append(dict(id=i, name=f'Test {i}'))
    for i in range(41, 51):
        result.append(dict(id=i, name=f'Test {i}'))

    return Response(
        headers={"Content-Type": "application/json"},
        status_code=status.HTTP_200_OK,
        content=json.dumps(result)
    )


@router_client.get("/get_data_source3", response_class=HTMLResponse)
async def get_data_source3():
    result = list()
    for i in range(21, 31):
        result.append(dict(id=i, name=f'Test {i}'))
    for i in range(51, 61):
        result.append(dict(id=i, name=f'Test {i}'))

    return Response(
        headers={"Content-Type": "application/json"},
        status_code=status.HTTP_200_OK,
        content=json.dumps(result)
    )


@router_client.get("/get_data_source4", response_class=HTMLResponse)
async def get_data_source4():
    result = list()
    #   останавливаем для теста таймаута
    await asyncio.sleep(2)
    for i in range(60, 90):
        result.append(dict(id=i, name=f'Test {i}'))

    return Response(
        headers={"Content-Type": "application/json"},
        status_code=status.HTTP_200_OK,
        content=json.dumps(result)
    )

