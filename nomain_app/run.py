import os

from main import app

if __name__ == '__main__':
    if os.getenv("DEBUG") == '1':
        app.run(port=8002, debug=True, host='0.0.0.0')
    else:
        app.run(port=8002, debug=False, host='0.0.0.0')
