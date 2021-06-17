from web3 import Web3
from ethtoken.abi import EIP20_ABI
import csv
import argparse

parser = argparse.ArgumentParser(description='Swarm Bee Batch transaction sender')
parser.add_argument('--input', '-i', help='输入csv文件', default="address_key.csv" )
parser.add_argument('--rpc', '-r', help='节点rpc', default='http://172.16.4.40:19000')
parser.add_argument('--key', '-k', help='转出eth和bzz的私钥')
args = parser.parse_args()

w3 = Web3(Web3.HTTPProvider(args.rpc))
# w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/b4ec9f1bed9b4f5fba50c0fc9776f1e5'))

#check connection
if w3.isConnected() is False:
    print("can not connect to RPC server.")
    exit()

chain_id = 5 #goerli
eth_initail_value = 0.1
gbzz_value = 1
gbzz_contract_addr = "0x2aC3c1d3e24b45c6C310534Bc2Dd84B5ed576335"
# from_private_key = "0x4429bb66e3a651652669effece888b05fe05022565158450e0260fda7cec6113"
from_private_key = args.key

account = w3.eth.account.privateKeyToAccount(from_private_key)
from_addr = account.address
startNonce = w3.eth.getTransactionCount(from_addr)

#estimate gas price
gasPriceWei = w3.eth.gasPrice
gasPrice = w3.fromWei(gasPriceWei + 10, 'gwei')  #a larger gas wei
print("current gasPrice:%d" % (gasPrice))

#gbzz conrtact
gbzz_contract = w3.eth.contract(address=gbzz_contract_addr, abi=EIP20_ABI)

i = 0

with open(args.input, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        to_addr = row[0]

        #1. Send gbzz
        gbzz_txn = gbzz_contract.functions.transfer(
            to_addr,
            gbzz_value * pow(10, 16),
        ).buildTransaction({
            'chainId': chain_id,
            'gas': 78394,
            'gasPrice': w3.toWei(gasPrice, 'gwei'),
            'nonce': startNonce + i,
        })

        signed_txn = w3.eth.account.signTransaction(gbzz_txn, from_private_key)

        tx = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        tx_hex = w3.toHex(tx)

        print("send from:%s to:%s gbzz value:%d hash:%s" %(from_addr, to_addr, gbzz_value, tx_hex))

        i = i + 1

        #2. Send geth
        eth_transaction = {
        'from': from_addr,
        'to': to_addr,
        'value': w3.toWei(0.1, "ether"),
        'gas': 21000,
        'gasPrice': w3.toWei(gasPrice, 'gwei'),
        'nonce': startNonce + i,
        'chainId': chain_id}

        signed_txn = w3.eth.account.signTransaction(eth_transaction, from_private_key)

        tx = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        tx_hex = w3.toHex(tx)

        print("send from:%s to:%s eth value:%f hash:%s" % (from_addr, to_addr, eth_initail_value, tx_hex))

        i = i + 1