import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException  # type: ignore
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RPC_USER = os.getenv("RPC_USER")
RPC_PASSWORD = os.getenv("RPC_PASSWORD")
RPC_PORT = os.getenv("RPC_PORT")
WALLET_NAME = os.getenv("WALLET_NAME")

RPC_URL = f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:{RPC_PORT}"

rpc_connection = AuthServiceProxy(RPC_URL)
print("\n✅ Connected to bitcoind\n")

# Create or Load Wallet
try:
    rpc_connection.loadwallet(WALLET_NAME)
    print(f"✅ Wallet '{WALLET_NAME}' loaded\n")
except JSONRPCException as e:
    if "not found" in str(e):
        rpc_connection.createwallet(WALLET_NAME)
        rpc_connection.loadwallet(WALLET_NAME)
        print(f"✅ Wallet '{WALLET_NAME}' created and loaded\n")
    elif "already loaded" in str(e):
        print(f"✅ Wallet '{WALLET_NAME}' already loaded\n")
    else:
        print(f"❌ Error loading wallet: {e}\n")

wallet_rpc = AuthServiceProxy(f"{RPC_URL}/wallet/{WALLET_NAME}")

# Generate Legacy Addresses
address_A = wallet_rpc.getnewaddress("", "legacy")
address_B = wallet_rpc.getnewaddress("", "legacy")
address_C = wallet_rpc.getnewaddress("", "legacy")

print(f"Address A: {address_A}")
print(f"Address B: {address_B}")
print(f"Address C: {address_C}\n")

# Fund Address A
try:
    amount = Decimal('0.5')
    txid = wallet_rpc.sendtoaddress(address_A, amount)
    print(f"✅ Funded Address A with {amount} BTC. TxID: {txid}\n")

    # ⛏️ Mine a block to confirm the transaction
    rpc_connection.generatetoaddress(1, address_A)
    print("✅ Transaction confirmed\n")
except JSONRPCException as e:
    print(f"❌ Error funding Address A: {e}\n")

# Create a Transaction from A to B
raw_tx = None
try:
    utxo = wallet_rpc.listunspent()
    if not utxo:
        raise Exception("No UTXO available for spending\n")

    selected_utxo = max(utxo, key=lambda x: x['amount'])
    available_amount = Decimal(selected_utxo['amount'])
    fee = Decimal('0.00001')
    send_amount = Decimal('0.5')
    change = available_amount - send_amount - fee
    
    inputs = [{
        "txid": selected_utxo['txid'],
        "vout": selected_utxo['vout']
    }]

    outputs = {address_B: float(send_amount)}
    if change > Decimal('0.00000546'):
        outputs[address_A] = float(change)

    raw_tx = wallet_rpc.createrawtransaction(inputs, outputs)
    print(f"✅ Raw Transaction Created\n")

except Exception as e:
    print(f"❌ Error creating transaction: {e}\n")

# Sign and Broadcast Transaction
if raw_tx:
    try:
        signed_tx = wallet_rpc.signrawtransactionwithwallet(raw_tx)
        if not signed_tx.get('complete'):
            raise Exception("Transaction signing failed\n")
        
        print(f"✅ Transaction Signed\n")
        
        txid = wallet_rpc.sendrawtransaction(signed_tx['hex'])
        print(f"✅ Transaction Broadcasted! TxID: {txid}\n")

        # Decode and Analyze Transaction
        decoded_tx = wallet_rpc.decoderawtransaction(signed_tx['hex'])
        print(f"✅ Decoded Transaction:\n{decoded_tx}\n")

        for vout in decoded_tx['vout']:
            if vout['scriptPubKey']['address'] == address_B:
                print(f"🔐 Locking Script for Address B:\n  {vout['scriptPubKey']['asm']}\n")

    except JSONRPCException as e:
        print(f"❌ Error broadcasting transaction: {e}\n")

# Final Wallet Balance
balance = wallet_rpc.getbalance()
print(f"💰 Final Wallet Balance: {balance:.8f} BTC\n")

# Mine a Block to Confirm Transaction
miner_address = wallet_rpc.getnewaddress("", "legacy")
block_hash = rpc_connection.generatetoaddress(1, miner_address)
print(f"✅ Block mined: {block_hash[0]}\n")

# Save Addresses
with open("addresses.txt", "w") as f:
    f.write(f"{address_A}\n{address_B}\n{address_C}")

print("✅ Task Complete!\n")
