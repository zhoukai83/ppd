from selenium import webdriver
import logging
import time
import os
import json
import logging.config

def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    logger = logging.getLogger(__name__)
    logger.info("start")
    return logger

def main():
    logger = logging.getLogger(__name__)
    driver = webdriver.Remote("http://127.0.0.1:9515", webdriver.DesiredCapabilities.CHROME);
    print(driver.command_executor._url)
    print(driver.session_id)
    driver.get("http://www.baidu.com")

    while True:
        time.sleep(100)

if __name__ == "__main__":
    # setup_logging()
    main()