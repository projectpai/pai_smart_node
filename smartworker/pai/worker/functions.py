import pathlib
import requests
import json

import yaml
from oben.aws.utils.exceptions import MessageProducerError
import config
from requests.auth import HTTPBasicAuth
from db.models import Ico
from sqlalchemy import create_engine


def connect_engine():
    DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

    BASE_DIR = pathlib.Path(__file__).parent
    config_path = BASE_DIR / 'db' / 'config.yaml'

    with open(str(config_path), 'rb') as f:
        db_config = yaml.load(f.read())

    conn = create_engine(DSN.format(**db_config['postgres_user']), isolation_level='AUTOCOMMIT').connect()

    return conn


def register_ico(**kwargs):
    required_params = ['asset', 'quantity', 'description', ]

    if not all(k in kwargs for k in required_params):
        raise MessageProducerError("Following parameters {} are required".format(required_params))

    conn = connect_engine()
    ico = Ico()
    try:
        response = ico.save_ico(conn=conn, **kwargs)
    except:
        pass

    return True


def get_all_icos():
    conn = connect_engine()
    ico = Ico()
    try:
        response = ico.get_all(conn=conn)
        print(response)
    except:
        pass


def get_ico_info(id):
    conn = connect_engine()
    ico = Ico()
    try:
        response = ico.get_by_id(conn, id)
    except:
        pass


def end_ico(id):
    conn = connect_engine()
    ico = Ico()
    try:
        response = ico.end_ico(conn, id)
    except:
        pass


def create_issuance(**kwargs):
    required_params = ["asset", "source", "quantity", "description"]

    if not all(k in kwargs for k in required_params):
        raise MessageProducerError("Following parameters {} are required".format(required_params))

    payload = {
        'method': 'create_issuance',
        'params': kwargs,
        'jsonrpc': '2.0',
        'id': 0
    }

    return counterparty_post(payload)


def send_asset(**kwargs):
    send_params = ['source', 'destination', 'asset', 'quantity']

    if not all(k in kwargs for k in send_params):
        raise MessageProducerError("Following parameters {} are required".format(send_params))

    payload = {
        'method': 'create_send',
        'params': kwargs,
        'jsonrpc': '2.0',
        'id': 0
    }

    return counterparty_post(payload)


def generate_new_account_address(**kwargs):
    if not kwargs.get('name'):
        raise MessageProducerError('Required name of account')

    payload = {
        "method": "generatenewaddress",
        "params": [kwargs.get("name")]
    }

    return paicoin_post(payload)


def counterparty_post(payload):
    url = 'http://{}:{}/api/'.format(config.RPC_CONNECT, config.RPC_PORT)
    auth = HTTPBasicAuth(config.RPC_USER, config.RPC_PASSWORD)
    headers = {
        'content-type': 'application/json'
    }
    try:
        response = requests.post(url=url, data=json.dumps(payload), auth=auth, headers=headers)
    except (requests.exceptions.SSLError,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError) as e:

        raise MessageProducerError(e)

    if response is None:
        raise MessageProducerError(
            'Cannot communicate with {}'.format(url))
    elif response.status_code not in (200, 500):
        msg = str(response.status_code) + ' ' + response.reason + ' ' + response.text
        raise MessageProducerError(msg)

    response_json = response.json()
    if 'error' not in response_json.keys() or response_json['error'] == None:
        response = response_json['result']
    else:
        raise MessageProducerError(response_json['error'])

    return response


def paicoin_post(payload):

    url = 'http://{}:{}@{}:{}'.format(config.WALLET_USER, config.WALLET_PASSWORD, config.WALLET_CONNECT,
                                      config.WALLET_PORT)
    headers = {'content-type': 'application/json'}

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response