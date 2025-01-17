from pathlib import Path
import json
import os

import datetime
import time

from web3 import Web3
from eth_typing import ChainId

from ledger_app_clients.ethereum.client import EthAppClient, StatusWord
from ledger_app_clients.ethereum.utils import get_selector_from_data
from ragger.navigator import NavInsID

from .utils import get_appname_from_makefile


ROOT_SCREENSHOT_PATH = Path(__file__).parent
ABIS_FOLDER = "%s/abis" % (os.path.dirname(__file__))
PLUGIN_NAME = get_appname_from_makefile()

with open("%s/0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D.abi.json" % (ABIS_FOLDER)) as file:
    contract = Web3().eth.contract(
        abi=json.load(file),
        # Get address from filename
        address=bytes.fromhex(os.path.basename(file.name).split(".")[0].split("x")[-1])
    )


# EDIT THIS: build your own test
def test_swap_exact_eth_for_token(backend, firmware, navigator, test_name):
    client = EthAppClient(backend)
    # print(client)

    data = contract.encodeABI("swapExactETHForTokens", [
        400000000,
        [
            bytes.fromhex("C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
            bytes.fromhex("A0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
        ],
        bytes.fromhex("d8dA6BF26964aF9D7eEd9e03E53415D37aA96045"),
        int(datetime.datetime(2024, 12, 25, 0, 0).timestamp())
    ])

    print("data: ", data)

    # first setup the external plugin
    with client.set_external_plugin(PLUGIN_NAME,
                                    contract.address,
                                    # Extract function selector from the encoded data
                                    get_selector_from_data(data)):
        pass

    # send the transaction
    with client.sign("m/44'/60'/1'/0/0", {
             "nonce": 20,
             "maxFeePerGas": Web3.to_wei(145, "gwei"),
             "maxPriorityFeePerGas": Web3.to_wei(1.5, "gwei"),
             "gas": 173290,
             "to": contract.address,
             "value": Web3.to_wei(2, "ether"),
             "chainId": ChainId.ETH,
             "data": data
         }):
    #     # Validate the on-screen request by performing the navigation appropriate for this device
        if firmware.device.startswith("nano"):
            navigator.navigate_until_text_and_compare(NavInsID.RIGHT_CLICK,
                                                      [NavInsID.BOTH_CLICK],
                                                      "Accept",
                                                      ROOT_SCREENSHOT_PATH,
                                                      test_name)
        else:
            navigator.navigate_until_text_and_compare(NavInsID.USE_CASE_REVIEW_TAP,
                                                      [NavInsID.USE_CASE_REVIEW_CONFIRM,
                                                       NavInsID.USE_CASE_STATUS_DISMISS],
                                                      "Hold to sign",
                                                      ROOT_SCREENSHOT_PATH,
                                                      test_name)
            

