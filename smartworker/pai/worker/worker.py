import json
import logging
import subprocess

import os
import requests
from oben.aws.utils.exceptions import MessageProducerError
from oben.aws.worker.abstract_worker import AbstractWorker
from requests.auth import HTTPBasicAuth
import config
from functions import create_issuance, send_asset, register_ico, get_all_icos


class SmartWorker(AbstractWorker):
    _allowed_methods = ['issuance', 'send', 'balances']

    def __init__(self):

        AbstractWorker.__init__(self)

        self.logger = None
        self.worker_id = None
        self.error = False
        self._worker_ip = subprocess.check_output(['hostname', '-i'])
        self._worker_environment = None
        self.root_nodes = ["redisData", "input"]

    def set_worker_id(self, worker_id, config_data=None):
        self.worker_id = worker_id

        logger_file = '/var/log/aws_worker/worker_{:02d}.log'.format(worker_id)
        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
                            datefmt='%Y-%m-%d,%H:%M:%S',
                            filename=logger_file,
                            filemode='w',
                            level=logging.INFO)
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.INFO)

    def _validate_incoming_message(self, message_data):

        for field_id in self.root_nodes:
            if field_id not in message_data:
                raise MessageProducerError("Incoming message does not contain {} field".format(field_id))

        if len(message_data) != len(self.root_nodes):
            raise MessageProducerError(
                "Incoming message contains unspecified fields.\nIt should contain only {}".format(
                    ', '.join(self.root_nodes)))

        if 'redisChannel' not in message_data['redisData']:
            raise MessageProducerError("Incoming message redisData must contain redisChannel field")

        if 'method' not in message_data['input']:
            raise MessageProducerError("Incoming message input must contain method name")

    def get_message_body(self, message):
        try:
            message_data = json.loads(message)
        except ValueError:
            self.logger.error("Incoming message couldn't not be json parsed")
            raise MessageProducerError("Incoming message couldn't not be json parsed")

        return message_data

    def process_message(self, message):
        self.error = False
        self.logger.info(message)

        message_body = self.get_message_body(message)
        self._validate_incoming_message(message_body)

        redis_channel = message_body['redisData']['redisChannel']
        self._status_reporting_provider.set_publish_channel(redis_channel)

        method = message_body['input']['method']
        params = message_body['input']['params']

        # TODO: Process message
        if method == 'register_ico':
            response = register_ico(**params)
        elif method == 'list_icos':
            response = get_all_icos()
        elif method == 'issuance':
            # do issuance
            response = create_issuance(**params)
        elif method == 'send':
            # send asset
            response = send_asset(**params)
        else:
            self.logger.error("Invalid method {}, use {} instead".format(method, self._allowed_methods))
            raise MessageProducerError("Invalid method {}, use {} instead".format(method, self._allowed_methods))

        self.publish_processing_status(100, 'Finished worker', response)

    def publish_processing_status(self, progress, update_text, response=None):

        message = {
            "SmartWorker": {
                "status": {
                    "status": "PENDING" if progress < 100 else "SUCCESS",
                    "progress": progress,
                    "message": update_text,
                },
                "output": {
                    "response": response
                },
                "worker_data": {
                    "workerIpAddress": self._worker_ip,
                    "workerEnvironment": self._worker_environment
                }

            }
        }

        json_status = json.dumps(message)

        self._status_reporting_provider.publish_message(json_status)
        self.logger.info("Publish update: %s" % json_status)

    def publish_processing_error(self, error_message: str):

        message = {
            "SmartWorker": {
                "status": {
                    "message": error_message,
                    "progress": 0,
                    "status": "ERROR"
                },
                "worker_data": {
                    'workerIpAddress': self._worker_ip,
                    "workerEnvironment": self._worker_environment
                }
            }

        }
        json_status = json.dumps(message)
        self._status_reporting_provider.publish_message(json_status)
        logger_message = 'Update: {}; Error: {}'.format(json_status, error_message)
        self.logger.error(logger_message)

    def compose_cli(self, method, params):

        signed_hex = params['signed_hex']
        url = 'http://{}:{}@{}:{}'.format(config.WALLET_USER, config.WALLET_PASSWORD, config.WALLET_CONNECT,
                                          config.WALLET_PORT)
        headers = {'content-type': 'application/json'}

        payload = json.dumps({"method": method, "params": signed_hex, "jsonrpc": "2.0"})
        response = requests.post(url, headers=headers, data=payload)
        return response


def main():
    """
    How Tall worker

    Configuration loading can be done in the following way

    python worker.py -e dev
    In the above way all configuration variables must be located in worker_conf.dev.yaml configuration

    python worker.py -e dev -u
    In the above way AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are loaded from environment variables
    and the rest will be loaded from worker_conf.dev.yaml

    python worker.py -e dev -a aws_access_key -s aws_secret_key
    In the above way AWS Access key and AWS Secret key are passed using command line and the rest is loaded using
    worker_conf.dev.conf

    Feel free to contact me for any additional questions
    """
    worker = SmartWorker()
    worker.load_configuration_based_on_command_line_parameters()
    worker.set_worker_id(worker_id=0)
    worker.start_listening()


if __name__ == '__main__':
    main()
