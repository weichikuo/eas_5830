from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
import json
import pandas as pd


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
    #YOUR CODE HERE
    w3 = connect_to(chain)
    this_contract_info = get_contract_info(chain, contract_info)

    this_contract = w3.eth.contract(
        address=Web3.to_checksum_address(this_contract_info["address"]),
        abi=this_contract_info["abi"]
    )

    latest_block = w3.eth.get_block_number()
    start_block = max(0, latest_block - 4)
    end_block = latest_block

    sk = "0x2c0021d8c5f31e3829e2ccdeea151b3aa829658398bd779a2ed7b4d951095728"

    if not sk.startswith("0x"):
        sk = "0x" + sk

    if chain == "source":
        # Listen for Deposit events on the source chain (Avalanche)
        event_filter = this_contract.events.Deposit.create_filter(
            from_block=start_block,
            to_block=end_block
        )
        events = event_filter.get_all_entries()

        # Connect to destination chain (BSC)
        other_w3 = connect_to("destination")
        other_contract_info = get_contract_info("destination", contract_info)
        other_contract = other_w3.eth.contract(
            address=Web3.to_checksum_address(other_contract_info["address"]),
            abi=other_contract_info["abi"]
        )

        acct = other_w3.eth.account.from_key(sk)
        nonce = other_w3.eth.get_transaction_count(acct.address, "pending")

        for evt in events:
            token = Web3.to_checksum_address(evt.args["token"])
            recipient = Web3.to_checksum_address(evt.args["recipient"])
            amount = evt.args["amount"]

            tx = other_contract.functions.wrap(
                token,
                recipient,
                amount
            ).build_transaction({
                "from": acct.address,
                "nonce": nonce,
                "gas": 300000,
                "gasPrice": other_w3.eth.gas_price,
                "chainId": other_w3.eth.chain_id
            })

            signed_tx = other_w3.eth.account.sign_transaction(tx, private_key=sk)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, "raw_transaction") else signed_tx.rawTransaction
            tx_hash = other_w3.eth.send_raw_transaction(raw_tx)
            other_w3.eth.wait_for_transaction_receipt(tx_hash)
            nonce += 1

    elif chain == "destination":
        # Listen for Unwrap events on the destination chain (BSC)
        event_filter = this_contract.events.Unwrap.create_filter(
            from_block=start_block,
            to_block=end_block
        )
        events = event_filter.get_all_entries()

        # Connect to source chain (Avalanche)
        other_w3 = connect_to("source")
        other_contract_info = get_contract_info("source", contract_info)
        other_contract = other_w3.eth.contract(
            address=Web3.to_checksum_address(other_contract_info["address"]),
            abi=other_contract_info["abi"]
        )

        acct = other_w3.eth.account.from_key(sk)
        nonce = other_w3.eth.get_transaction_count(acct.address, "pending")

        for evt in events:
            token = Web3.to_checksum_address(evt.args["underlying_token"])
            recipient = Web3.to_checksum_address(evt.args["to"])
            amount = evt.args["amount"]

            tx = other_contract.functions.withdraw(
                token,
                recipient,
                amount
            ).build_transaction({
                "from": acct.address,
                "nonce": nonce,
                "gas": 300000,
                "gasPrice": other_w3.eth.gas_price,
                "chainId": other_w3.eth.chain_id
            })

            signed_tx = other_w3.eth.account.sign_transaction(tx, private_key=sk)
            raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, "raw_transaction") else signed_tx.rawTransaction
            tx_hash = other_w3.eth.send_raw_transaction(raw_tx)
            other_w3.eth.wait_for_transaction_receipt(tx_hash)
            nonce += 1
