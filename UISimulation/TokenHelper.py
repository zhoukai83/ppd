import json
import datetime


def get_token_from_config():
    with open('Token.json') as f:
        data = json.load(f)
        token_update_time = datetime.datetime.strptime(str(data["TokenUpdateTime"]), "%Y-%m-%d %H:%M:%S.%f")
        return token_update_time, data


def save_token_into_config(token_info):
    with open('Token.json', "r+") as f:
        f.seek(0)
        f.write(json.dumps(token_info, indent=4))


def refresh_open_client_token(ppd_open_client, token_config, logger):
    result = ppd_open_client.refresh_token(token_config["OpenId"], token_config["RefreshToken"])
    logger.info(f"need update client token: {result}")
    json_data = json.loads(result)

    json_data["TokenUpdateTime"] = str(datetime.datetime.now())
    json_data["OpenId"] = token_config["OpenId"]
    save_token_into_config(json_data)
    token_update_time = datetime.datetime.now()
    return token_update_time, json_data