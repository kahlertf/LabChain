import argparse
import logging
import os

# append project dir to python path
from labchain.util.cryptoHelper import CryptoHelper
from labchain.network.networking import ClientNetworkInterface, JsonRpcClient
from labchain.blockchainClient import Wallet, BlockchainClient
from labchain.workflow.workflowClient import WorkflowClient

# set TERM environment variable if not set
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm-color'

CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
WALLET_FILE_PATH = os.path.join(CONFIG_DIRECTORY, 'wallet.csv')


def create_config_directory():
    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)


def create_client(wallet_file, node_ip, node_port):
    crypto_helper = CryptoHelper.instance()
    network_interface = ClientNetworkInterface(JsonRpcClient(), {node_ip: {node_port: {}}})
    return BlockchainClient(Wallet(wallet_file), network_interface, crypto_helper)


def create_document_flow_client(wallet_file, node_ip, node_port):
    crypto_helper = CryptoHelper.instance()
    network_interface = ClientNetworkInterface(JsonRpcClient(), {node_ip: {node_port: {}}})
    return WorkflowClient(Wallet(wallet_file), network_interface, crypto_helper)


def setup_logging(verbose, very_verbose):
    if very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser(description='CLI client for Labchain.')
    parser.add_argument('node_ip', nargs='?',help='The IP address of the Labchain node',default="localhost")
    parser.add_argument('node_port',nargs='?',help='The port address of the Labchain node',default="8080")
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--very-verbose', '-vv', action='store_true')
    parser.add_argument('--doc', help='Use this argument if you want to use the document flow client.', action='store_true')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args.verbose, args.very_verbose)
    create_config_directory()
    if os.path.exists(WALLET_FILE_PATH):
        file_mode = 'r+'
    else:
        file_mode = 'w+'
    with open(WALLET_FILE_PATH, file_mode) as open_wallet_file:
        if args.doc:
            client = create_document_flow_client(open_wallet_file, args.node_ip, args.node_port)
            client.main()
        else:
            client = create_client(open_wallet_file, args.node_ip, args.node_port)
            client.main()

def create_document_flow_client_instance():
    args = parse_args()
    create_config_directory()
    if os.path.exists(WALLET_FILE_PATH):
        file_mode = 'r+'
    else:
        file_mode = 'w+'
    with open(WALLET_FILE_PATH, file_mode) as open_wallet_file:
        return create_document_flow_client(open_wallet_file, args.node_ip, args.node_port)