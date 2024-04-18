#'6952664913:AAFKIVK5zmmeMU7pyuTdUp1W3bgrwyYHjwE'
Channels = ['https://t.me/allsecretton -1001912673914']

Group_id = ['-1001912673914']

Admin_ids = [6248577556, 838970024, 1255314241]
# 838970024


user_name_bot = 'allsecretton_bot'

# 763283309,


import yaml


def save_secrets(secrets: dict):
    with open("secrets.yaml", "w") as stream:
        yaml.dump(secrets, stream, default_flow_style=False)


def check_chat_id(chat_id):
    with open("sercets.yaml", "r") as stream:
        try:
            secrets = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    if chat_id in secrets['secrets']['chat_ids']:
        return False
    else:
        return True


def read_secrets():
    with open("secrets.yaml", "r") as stream:
        try:
            secrets = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return secrets

from os import environ as env

from dotenv import load_dotenv
load_dotenv()

TOKEN = TOK = env['TOKEN']
MANIFEST_URL = env['MANIFEST_URL']


