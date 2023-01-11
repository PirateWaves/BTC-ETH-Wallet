# Multi-Blockchain Wallet in Python

![newtons-coin-cradle](Images/newtons-coin-cradle.jpg)

## Background

Your new startup is focusing on building a portfolio management system that supports not only traditional assets
like gold, silver, stocks, etc, but crypto-assets as well! The problem is, there are so many coins out there! It's
a good thing you understand how HD wallets work, since you'll need to build out a system that can create them.

You're in a race to get to the market. There aren't as many tools available in Python for this sort of thing, yet.
Thankfully, you've found a command line tool, `hd-wallet-derive` that supports not only BIP32, BIP39, and BIP44, but
also supports non-standard derivation paths for the most popular wallets out there today! However, you need to integrate
the script into your backend with your dear old friend, Python.

Once you've integrated this "universal" wallet, you can begin to manage billions of addresses across 300+ coins, giving
you a serious edge against the competition.

In this assignment, however, I will only need to get 2 coins working: Ethereum and Bitcoin Testnet.
Ethereum keys are the same format on any network, so the Ethereum keys should work with your custom networks or testnets.

## Dependencies

- PHP must be installed on your operating system (any version, 5 or 7). Don't worry, you will *not* need to know any PHP.

- You will need to clone the [`hd-wallet-derive`](https://github.com/dan-da/hd-wallet-derive) tool.

- [`bit`](https://ofek.github.io/bit/) Python Bitcoin library.

- [`web3.py`](https://github.com/ethereum/web3.py) Python Ethereum library.

## Instructions

### Project setup

- Create a project directory called `wallet` and `cd` into it.

- Clone the `hd-wallet-derive` tool into this folder and install it using the instructions on its `README.md`.

- Create a symlink called `derive` for the `hd-wallet-derive/hd-wallet-derive.php` script into the top level project
  directory like so: `ln -s hd-wallet-derive/hd-wallet-derive.php derive`

  This will clean up the command needed to run the script in our code, as we can call `./derive`
  instead of `./hd-wallet-derive/hd-wallet-derive.php`.

- Test that you can run the `./derive` script properly, use one of the examples on the repo's `README.md`

- Create a file called `wallet.py` -- this will be your universal wallet script.

Your directory tree should look something like this:

![directory-tree](Images/tree.png)

### 1. Setup constants

- In a separate file, `constants.py`, set the following constants:
  - `BTC = 'btc'`
  - `ETH = 'eth'`
  - `BTCTEST = 'btc-test'`

- In `wallet.py`, import all constants: `from constants import *`

- Use these anytime you reference these strings, both in function calls, and in setting object keys.

### 2. Generate a Mnemonic

- Generate a new 12 word mnemonic using `hd-wallet-derive` or by using [this tool](https://iancoleman.io/bip39/).

- Set this mnemonic as an environment variable, and include the one you generated as a fallback using:
  `mnemonic = os.getenv('MNEMONIC', 'insert mnemonic here')`

```python
mnemonic = os.getenv('MNEMONIC')
print(mnemonic)
```
### 3. Deriving the wallet keys

- Use the `subprocess` library to call the `./derive` script from Python. Make sure to properly wait for the process.

- The following flags must be passed into the shell command as variables:
  - Mnemonic (`--mnemonic`) must be set from an environment variable, or default to a test mnemonic
  - Coin (`--coin`)
  - Numderive (`--numderive`) to set number of child keys generated

- Set the `--format=json` flag, then parse the output into a JSON object using `json.loads(output)`

- You should wrap all of this into one function, called `derive_wallets`

- Create an object called `coins` that derives `ETH` and `BTCTEST` wallets with this function.
  When done properly, the final object should look something like this (there are only 3 children each in this image):

```python
def derive_wallets(mnem,coinname,num):
    command = './derive -g --mnemonic="'+str(mnem)+'"   --numderive=""'+str(num)+'"" --coin=""'+str(coinname)+'"" --format=jsonpretty'
    p = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
    (output, err) = p.communicate()
    return json.loads(output)
```
```python
coins = {ETH:derive_wallets(mnem=mnemonic,coinname=ETH,num=3),BTCTEST: derive_wallets(mnem=mnemonic,coinname=BTCTEST,num=3)}
```
![wallet-object](Images/drivekeys.png)

You should now be able to select child accounts (and thus, private keys) by calling `coins[COINTYPE][INDEX]['privkey']`.

### POW Linking the transaction signing libraries

Now, we need to use `bit` and `web3.py` to leverage the keys we've got in the `coins` object.
You will need to create three more functions:

- `priv_key_to_account` -- this will convert the `privkey` string in a child key to an account object
  that `bit` or `web3.py` can use to transact.
  This function needs the following parameters:

  - `coin` -- the coin type (defined in `constants.py`).
  - `priv_key` -- the `privkey` string will be passed through here.

  You will need to check the coin, then return one of the following functions based on the library:

  - For `ETH`, return `Account.privateKeyToAccount(priv_key)`
  - For `BTCTEST`, return `PrivateKeyTestnet(priv_key)`

- `create_tx` -- this will create the raw, unsigned transaction that contains all metadata needed to transact.
  This function needs the following parameters:

  - `coin` -- the coin type (defined in `constants.py`).
  - `account` -- the account object from `priv_key_to_account`.
  - `to` -- the recipient address.
  - `amount` -- the amount of the coin to send.

  - For `ETH`, return an object containing `to`, `from`, `value`, `gas`, `gasPrice`, `nonce`, and `chainID`.
    Make sure to calculate all of these values properly using `web3.py`!
  - For `BTCTEST`, return `PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])`

- `send_tx` -- this will call `create_tx`, sign the transaction, then send it to the designated network.
  This function needs the following parameters:

  - `coin` -- the coin type (defined in `constants.py`).
  - `account` -- the account object from `priv_key_to_account`.
  - `to` -- the recipient address.
  - `amount` -- the amount of the coin to send.

  You may notice these are the exact same parameters as `create_tx`. `send_tx` will call `create_tx`, so it needs
  all of this information available.

  You will need to check the coin, then create a `raw_tx` object by calling `create_tx`. Then, you will need to sign
  the `raw_tx` using `bit` or `web3.py` (hint: the account objects have a sign transaction function within).

  Once you've signed the transaction, you will need to send it to the designated blockchain network.

  - For `ETH`, return `w3.eth.sendRawTransaction(signed.rawTransaction)`
  - For `BTCTEST`, return `NetworkAPI.broadcast_tx_testnet(signed)`
```python
def priv_key_to_account (coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

def create_raw_tx(account, recipient, amount):
    gasEstimate = web3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount}
    )
    return {
        "from": account.address,
        "to": recipient,
        "value": amount,
        "gasPrice": web3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": web3.eth.getTransactionCount(account.address),
    }
def create_tx(coin,account,to,amount):
    if (coin==ETH):
        return create_raw_tx(account,to,amount)
    else:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
  You will need to check the coin, then return one of the following functions based on the library:

def send_tx (coin, account, recipient, amount):
    if coin =='ETH':
        trxns_eth = create_tx(coin,account, recipient, amount)
        sign_trxns_eth = account.sign_transaction(trxns_eth)
        result = w3.eth.sendRawTransaction(sign_trxns_eth.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        trxns_btctest= create_tx(coin,account,recipient,amount)
        sign_trxns_btctest = account.sign_transaction(trxns_btctest)
        NetworkAPI.broadcast_tx_testnet(sign_trxns_btctest)       
        return tx_hex

```



### Sending Transactions

For Bitcoin: Now, you should be able to fund these wallets using testnet faucets. Open up a new terminal window inside of `wallet`,
then run `python`. Within the Python shell, run

```python
`from wallet import *`
```
-- you can now access the functions interactively.
You'll need to set the account with  `priv_key_to_account` and use `send_tx` to send transactions.

#### Bitcoin Testnet transaction

- Fund a `BTCTEST` address using [this testnet faucet](https://coinfaucet.eu/en/btc-testnet/).

- Use a [block explorer](https://tbtc.bitaps.com/) to watch transactions on the address.

- Send a transaction to another testnet address (either one of your own, or the faucet's).

- Screenshot the confirmation of the transaction like so:

![btc-test](Images/btctestsuccess.png)

#### Local PoA Ethereum transaction

- Running with POA I found it diffuclt to use the above code instead I ran the below code in Python:

Steps for Local Set Up:

1. Add one of the `ETH` addresses to the pre-allocated accounts in your `networkname.json`. As well as to a sealer address to be a validator and be pre-funded.  
2. Go to MyCrypto - for the pre-allocated accounts use the private key under your custom network to download the UTC-key. Create a password for the custom `ETH` address.
3. Under 'Blockchain Tools' create a new folder node3 , I use node3 as I had origniall started two new accounts when intitliazing my nodes. See github link. (https://github.com/KeepItOnTheDownload/Multi-Blockchain_Wallet-)
4. I add the UTC file I just downloaded into the folder and add a password.txt file for the password created in MyCrypto.

- Delete the `geth` folder in each node that you ran previously (if you are starting from scratch then ingore this step), then re-initialize

5.  Initialize the new node, and any other nodes that have been created.
```Python
#Tis will create a new chain, and will pre-fund the new account.
`geth --datadir nodeX init networkname.json`.
```

6. Mine the node with the address added

```Python
./geth --datadir node3 --mine --minerthreads 1 --unlock "df460bD851a7540c70BeE83E5bA1b63410c4F220" --password node3/password.txt  --rpc --allow-insecure-unlock
```
7. Mine the second node2 (created from a local new account) with the encoding address of node3
```Python
./geth --datadir node2 --unlock "22aD648e49B7E09148dCB29CF6a09888e6fB44E3" --mine --port 30305 --bootnodes enode://9027de1e56f0d03ee3ccc07e3860c1ba3154c3a07ccdc92bc4bed04b9b8bb41c48edea8862b089c132a86d1ff28c0926f48d9089e58965964a4a867c2259c29a@127.0.0.1:30303 --password node2/password.txt  --allow-insecure-unlock
```

8. Use the following code in Python and check in MyCrypto using the hash if successful!

```Python
account1 = 'your account address'
account2 = 'your account address'

privatekey = 'account one private key'

nonce = web3.eth.getTransactionCount(account1)

tx = {
    'nonce': nonce,
    'to': account2,
    'value': web3.toWei(10, 'ether'),
    'gas': 2000000,
    'gasPrice': web3.toWei('50', 'gwei'),
}
signed_tx = web3.eth.account.signTransaction(tx, privatekey)

tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
print(web3.toHex(tx_hash))
```


- Send a transaction from the pre-funded address within the wallet to another, then copy the `txid` into
  MyCrypto's TX Status, and screenshot the successful transaction like so:

![eth-hash](Images/tx_has.png)
![eth-test](Images/SUCCESSFUL.png)


### Challenge Mode

- Add support for `BTC`.

- Add support for `LTC` using the sister library, [`lit`](https://github.com/blockterms/lit).

- Add a function to track transaction status by `txid`.
