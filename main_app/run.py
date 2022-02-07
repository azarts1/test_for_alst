import os

import uvicorn

if __name__ == '__main__':
    if os.getenv("DEBUG") == '1':
        uvicorn.run('main:app', reload=True, port=8001, host='0.0.0.0')
    else:
        uvicorn.run('main:app', reload=False, port=8001, host='0.0.0.0')
