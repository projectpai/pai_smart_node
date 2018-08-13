import pathlib

import os
import requests
import json
import sqlalchemy.exc
import yaml
from oben.aws.utils.exceptions import MessageProducerError
import config
from requests.auth import HTTPBasicAuth
from db.models import Ico, Transaction

USER_DIR = os.path.expanduser('~')
ICO_CONFIG_DIR = os.path.join(USER_DIR, '.ico', 'config')


def register_ico(**kwargs):
    """
    :param message:
        {
            "redisData": {
              "redisChannel": "id"
            },
            "input": {
              "method": "register_ico",
              "params": {
                "return_address": "PiJgSZgm2z5EhBg4msPXCxL3W2DMhP9ihV",
                "quantity": 10000000,
                "asset": "TRUEBTC",
                "price": 1,
                "start_date": "2018-08-31 12:00:00",
                "end_date": "2018-08-31 12:00:00",
                "hard_cap": 1000000000,
                "soft_cap": 100000000000,
                "details": {
                    "description": "Some TRUE description"
                 }
              }
            }
        }
    :return:
    address
    (?????)
    """
    # TODO: Add more parameters
    required_params = ['return_address', 'asset', 'quantity', 'price', 'start_date', 'end_date', 'hard_cap', 'soft_cap']

    # STEP 1: validation
    # TODO: Improve validation
    # check for required params
    for required_param in required_params:
        if required_param not in kwargs:
            raise MessageProducerError("Following parameter `{}` is required".format(required_param))

    # STEP 2: Generate associated address for income transactions in smartnode paicoin
    address = generate_address(kwargs.get('return_address'))

    # STEP 3: Save to ICO model
    params = {
        'asset': kwargs.get('asset'),
        'return_address': kwargs.get('return_address'),
        'source_address': address,
        'details': json.dumps(kwargs.get('details')) if kwargs.get('details') else None
    }
    try:
        ico = Ico()
        ico.save_ico(**params)
    except sqlalchemy.exc.IntegrityError as e:
        raise MessageProducerError(e)

    # STEP 4: Create config
    if not os.path.exists(ICO_CONFIG_DIR):
        os.makedirs(ICO_CONFIG_DIR)

    ico_config_path = os.path.join(ICO_CONFIG_DIR, address)
    if not os.path.exists(ico_config_path):
        os.mkdir(ico_config_path)
    # config
    ico_config = {
        'required_parameters': {
            'asset': kwargs.get('asset'),
            'quantity': kwargs.get('quantity'),
            'description': kwargs.get('description'),
            'source_address': address,
            'return_address': kwargs.get('return_address'),
            'price': kwargs.get('price'),
            'start_date': kwargs.get('start_date'),
            'end_date': kwargs.get('start_date'),
            'auto_payments': kwargs.get('auto_payments') if kwargs.get('auto_payments') else True,
        },
        'optional_parameters': {
            'soft_cap': kwargs.get('soft_cap'),
            'hard_cap': kwargs.get('hard_cap'),
            'asset_long_name': kwargs.get('asset_long_name')
        },
        'additional_parameters': {
            'details': kwargs.get('details')
        }
    }
    with open(os.path.join(ico_config_path, '{}.conf.json'.format(kwargs.get('asset'))), 'w+') as file:
        json.dump(ico_config, file, indent=4)

    return address


def get_all_icos():
    """
    :param message:
        {
            "redisData": {
              "redisChannel": "id"
            },
            "input": {
              "method": "list_ico",
              "params": []
            }
        }
    :return:
    address
    ico_list
    """
    ico = Ico()
    res = ico.get_all()
    # TODO: add ico config import
    return res


def get_ico_info(id):
    ico = Ico()
    return ico.get_by_id(id)


def end_ico(id):
    ico = Ico()
    response = ico.end_ico(id)


def create_issuance(**kwargs):
    """
    :param kwargs:
     {
        "redisData": {
          "redisChannel": "id"
        },
        "input": {
          "method": "issuance",
          "params": {
            "source": "PhGWKbvaTdU7MMgmuktGCaVQN93Rxvye7d",
            "quantity": 10000000000,
            "asset": "TRUEBTC5",
            "description": "Some desc here"
          }
        }
    }
    :return:
    signed tx hex
    """
    required_params = ["asset", "source", "quantity", "description"]

    # STEP 1: validation
    # TODO: Improve validation
    # 1.1 check for required params
    for required_param in required_params:
        if required_param not in kwargs:
            raise MessageProducerError("Following parameter `{}` is required".format(required_param))

    # 1.2 check for registered address
    ico = Ico()
    ico_info = ico.get_by_source_address(kwargs.get('source'))

    if not ico_info:
        # not registered attempt
        raise MessageProducerError(
            "Following address `{}` is not registered as ICO address".format(kwargs.get('source')))

    if not ico_info['is_approved']:
        raise MessageProducerError(
            "Following ICO {} on `{}` address is not approved".format(ico_info['asset'], kwargs.get('source')))

    # STEP 2: create_issuance in party
    payload = {
        'method': 'create_issuance',
        'params': kwargs,
        'jsonrpc': '2.0',
        'id': 0
    }
    # unsigned tx hex
    unsigned_tx_hex = counterparty_post(payload)
    # STEP 3: Sign and Send to the paicoin blockchain
    signed_tx_hex = sign_and_send(unsigned_tx_hex)
    return signed_tx_hex


def send_asset(**kwargs):
    """
    :param kwargs:
     {
        "redisData": {
          "redisChannel": "id"
        },
        "input": {
          "method": "send",
          "params": {
            "source": "PhGWKbvaTdU7MMgmuktGCaVQN93Rxvye7d",
            "destination": "PhGWKbvaTdU7MMgmuktGCaVQN93Rxvye7d",
            "quantity": 10,
            "asset": "TRUEBTC5",
          }
        }
    }
    :return:
    signed tx hex
    """
    send_params = ['source', 'destination', 'asset', 'quantity']

    if not all(k in kwargs for k in send_params):
        raise MessageProducerError("Following parameters {} are required".format(send_params))

    payload = {
        'method': 'create_send',
        'params': kwargs,
        'jsonrpc': '2.0',
        'id': 0
    }
    # TODO: add response validation
    unsigned_tx_hex = counterparty_post(payload)
    return sign_and_send(unsigned_tx_hex)


def get_unpaid_transactions(source):
    allowed_filters = ['unpaid']

    # get unpaid transactions
    transaction = Transaction()
    return transaction.get_unpaid(source)


def pay_unpaid_transactions(ico_id, tr_list):
    # load ico
    ico = Ico()
    ico_info = ico.get_by_id(ico_id)
    tx_ids = []
    for transaction in tr_list:
        source_address = transaction['asset_address']
        destination_address = transaction['contributor_address']
        # amount_to_send
        amount_to_send = transaction['amount'] * ico_info['price']
        asset = ico_info['asset']

        unsigned_tx_hex = send_asset(source=source_address, destination=destination_address, asset=asset,
                                     quantity=amount_to_send)
        tx_id = sign_and_send(unsigned_tx_hex)
        tx_ids.append(tx_id)

    return tx_ids


def import_address(name, address):
    payload = {
        "method": "importaddress",
        "params": [address, name]
    }
    paicoin_post(payload)


def generate_address(return_address):
    payload = {
        "method": "getaccountaddress",
        "params": [return_address]
    }

    response = paicoin_post(payload)
    if response.status_code in [200, 500]:
        response_json = response.json()

        return response_json['result']


def sign_and_send(unsigned_tx_hex):
    sign_payload = {
        'method': 'signrawtransaction',
        'params': [unsigned_tx_hex]
    }
    # FIXME: Update responses in paicoin
    response = paicoin_post(sign_payload)
    if response.status_code in [200, 500]:
        response_json = response.json()
        signed_hex = response_json['result']['hex']
        # STEP 3.2: send raw transaction

        send_payload = {
            'method': 'sendrawtransaction',
            'params': [signed_hex]
        }

        response = paicoin_post(send_payload)
        if response.status_code in [200, 500]:
            response_json = response.json()
            tx_id = response_json['result']

            return tx_id
    else:
        raise MessageProducerError('Could not communicate with paicoin rpc server')


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

    # TODO: Add response validation
    return response
