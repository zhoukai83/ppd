from flask import Flask
app = Flask(__name__)

import logging
import requests

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)

    # app.run(host='0.0.0.0')
    logger.info("start")
    # t = requests.get("http://10.102.87.166:5000/")
    t = requests.get("http://127.0.0.1:5000")
    logger.info(t.text)