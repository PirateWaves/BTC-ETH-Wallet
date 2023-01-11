#Import Dependecies
import subprocess
import json
import os

from constants import *
from web3 import Web3
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from eth_account import Account
from pathlib import Path
from getpass import getpass
from constants import *
load_dotenv()
from bit import *
from bit import Key
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI

#Initiate Web3 object
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

#Set as an Environment Variable at first

mnemonic = os.getenv('MNEMONIC')
print(mnemonic)

# Derive Wallet Function here you can set the coins you want to pull the amount of addresses
def derive_wallets(mnem,coinname,num):
    command = './derive -g --mnemonic="'+str(mnem)+'" --numderive=""'+str(num)+'"" --coin=""'+str(coinname)+'"" --format=jsonpretty'
    p = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
    (output, err) = p.communicate()
    return json.loads(output)

# In this example we only test BTCTEST and ETH however in further code would be better
# to loop through coins{}
coins = {ETH:derive_wallets(mnem=mnemonic,coinname=ETH,num=3),BTCTEST: derive_wallets(mnem=mnemonic,coinname=BTCTEST,num=3)}

def priv_key_to_account (coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

eth_pk_acct1 = priv_key_to_account(ETH,coins['eth'][0]['privkey'])
eth_pk_acct2 = priv_key_to_account(ETH, coins['eth'][1]['privkey'])
eth_pk_acct3 = priv_key_to_account(ETH, coins['eth'][2]['privkey'])

btc_pk_acct1 = priv_key_to_account('btc-test',coins['btc-test'][0]['privkey'])
btc_pk_acct2 = priv_key_to_account('btc-test',coins['btc-test'][1]['privkey'])

def create_raw_tx(account, recipient, amount):
    gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount}
    )
    return {
        "from": account.address,
        "to": recipient,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
    }

def create_tx(coin,account, to, amount):
    if (coin==ETH):
        return create_raw_tx(account,to,amount)
    else:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, recipient, amount):
    tx = create_tx(coin,account, recipient, amount)
    signed_tx = account.sign_transaction(tx)
    result=None
    if(coin==ETH):
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    else:
        result= NetworkAPI.broadcast_tx_testnet(signed_tx)
    return result
