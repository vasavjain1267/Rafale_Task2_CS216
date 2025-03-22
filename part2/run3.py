import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException # type: ignore
from decimal import Decimal
from dotenv import load_dotenv

# Step 1: Connect to bitcoind
load_dotenv()

RPC_USER = os.getenv("RPC_USER")
RPC_PASSWORD = os.getenv("RPC_PASSWORD")
RPC_PORT = os.getenv("RPC_PORT")

RPC_URL = f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:{RPC_PORT}"

rpc_connection = AuthServiceProxy(RPC_URL)
print("\n✅ Connected to bitcoind\n")

# Step 2: Create or Load Wallet
WALLET_NAME = os.getenv("WALLET_NAME")
try:
    # Try to load the wallet
    rpc_connection.loadwallet(WALLET_NAME)
    print(f"✅ Wallet '{WALLET_NAME}' loaded\n")
except JSONRPCException as e:
    if "not found" in str(e):
        # Create the wallet if it doesn't exist
        rpc_connection.createwallet(WALLET_NAME)
        rpc_connection.loadwallet(WALLET_NAME)
        print(f"✅ Wallet '{WALLET_NAME}' created and loaded\n")
    elif "already loaded" in str(e):
        print(f"✅ Wallet '{WALLET_NAME}' already loaded\n")
    else:
        print(f"❌ Error loading wallet: {e}\n")

# Create a connection to the specific wallet
wallet_rpc = AuthServiceProxy(f"{RPC_URL}/wallet/{WALLET_NAME}")

# Step 3: Generate P2SH-SegWit Addresses
address_A = wallet_rpc.getnewaddress("", "p2sh-segwit")
address_B = wallet_rpc.getnewaddress("", "p2sh-segwit")
address_C = wallet_rpc.getnewaddress("", "p2sh-segwit")

print(f"Address A': {address_A}")
print(f"Address B': {address_B}")
print(f"Address C': {address_C}\n")

# Step 3.1: Fund Address A'
amount = Decimal('0.5')
try:
    # Send BTC to Address A'
    txid = wallet_rpc.sendtoaddress(address_A, amount)
    print(f"✅ Funded Address A' with {amount} BTC. TxID: {txid}\n")

    # Mine a block to confirm the transaction
    miner_address = wallet_rpc.getnewaddress("", "legacy")
    block_hash = rpc_connection.generatetoaddress(1, miner_address)
    print(f"✅ Transaction confirmed (Block mined: {block_hash[0]})\n")
except JSONRPCException as e:
    print(f"❌ Error funding Address A': {e}\n")

# Step 4: Create Transaction from A' to B'
try:
    # Get unspent UTXO from Address A'
    utxos = wallet_rpc.listunspent()
    utxo = next((u for u in utxos if u['address'] == address_A), None)
    if not utxo:
        raise Exception(f"No spendable UTXO found for {address_A}\n")

    available_amount = Decimal(utxo['amount'])
    send_amount = Decimal('0.3')
    fee = Decimal('0.00001')
    change = available_amount - send_amount - fee

    # Create inputs and outputs for the transaction
    inputs = [{
        "txid": utxo['txid'],
        "vout": utxo['vout']
    }]
    outputs = {address_B: float(send_amount)}

    # Send change back to Address A' if there's enough left after fees
    if change > Decimal('0.00000546'):
        outputs[address_A] = float(change)

    # Create raw transaction
    raw_tx = wallet_rpc.createrawtransaction(inputs, outputs)
    print(f"✅ Raw Transaction Created\n")

    # Sign the transaction using the wallet's private key
    signed_tx = wallet_rpc.signrawtransactionwithwallet(raw_tx)
    if not signed_tx.get('complete'):
        raise Exception("Transaction signing failed\n")

    # Broadcast the signed transaction
    txid = wallet_rpc.sendrawtransaction(signed_tx['hex'])
    print(f"✅ Transaction Broadcasted! TxID: {txid}\n")

    # Decode the transaction and extract the locking script for B'
    decoded_tx = wallet_rpc.decoderawtransaction(signed_tx['hex'])
    print(f"✅ Decoded Transaction:\n{decoded_tx}\n")

    for vout in decoded_tx['vout']:
        if vout['scriptPubKey']['address'] == address_B:
            print(f"🔐 Locking Script for Address B':\n  {vout['scriptPubKey']['asm']}\n")

except Exception as e:
    print(f"❌ Error creating or broadcasting transaction: {e}\n")

# Mine a block to confirm the transaction
miner_address = wallet_rpc.getnewaddress("", "legacy")
block_hash = rpc_connection.generatetoaddress(1, miner_address)
print(f"✅ Block mined: {block_hash[0]}\n")

# Step 5: Create Transaction from B' to C'
try:
    # Get unspent UTXO from Address B'
    utxos = wallet_rpc.listunspent()
    utxo_B = next((u for u in utxos if u['address'] == address_B), None)
    if not utxo_B:
        raise Exception(f"No spendable UTXO found for {address_B}\n")

    available_amount = Decimal(utxo_B['amount'])
    send_amount = Decimal('0.2')
    fee = Decimal('0.00001')
    change = available_amount - send_amount - fee

    # Create inputs and outputs for the transaction
    inputs = [{
        "txid": utxo_B['txid'],
        "vout": utxo_B['vout']
    }]
    outputs = {address_C: float(send_amount)}

    # Send change back to Address B' if there's enough left after fees
    if change > Decimal('0.00000546'):
        outputs[address_B] = float(change)

    # Create raw transaction
    raw_tx = wallet_rpc.createrawtransaction(inputs, outputs)
    print(f"✅ Raw Transaction Created\n")

    # Sign the transaction using the wallet's private key
    signed_tx = wallet_rpc.signrawtransactionwithwallet(raw_tx)
    if not signed_tx.get('complete'):
        raise Exception("Transaction signing failed\n")

    # Broadcast the signed transaction
    txid = wallet_rpc.sendrawtransaction(signed_tx['hex'])
    print(f"✅ Transaction Broadcasted! TxID: {txid}\n")

    # Decode the transaction and extract the scripts
    decoded_tx = wallet_rpc.decoderawtransaction(signed_tx['hex'])
    print(f"✅ Decoded Transaction:\n{decoded_tx}\n")

    # Display unlocking script (scriptSig) and locking script (scriptPubKey)
    for vin in decoded_tx['vin']:
        print(f"🔒 ScriptSig (Unlocking Script): {vin['scriptSig']['asm']}")
        print(f"ScriptSig (Hex): {vin['scriptSig']['hex']}\n")

    for vout in decoded_tx['vout']:
        if vout['scriptPubKey']['address'] == address_C:
            print(f"🔑 ScriptPubKey (Locking Script) for Address C': {vout['scriptPubKey']['asm']}")
            print(f"ScriptPubKey (Hex): {vout['scriptPubKey']['hex']}\n")

except Exception as e:
    print(f"❌ Error creating or broadcasting transaction: {e}\n")

# Step 6: Final Wallet Balance
balance = wallet_rpc.getbalance()
print(f"💰 Final Wallet Balance: {balance:.8f} BTC\n")

# Mine a block to confirm the transaction
block_hash = rpc_connection.generatetoaddress(1, miner_address)
print(f"✅ Block mined: {block_hash[0]}\n")

# Step 7: Save Addresses
with open("addresses.txt", "w") as f:
    f.write(f"{address_A}\n{address_B}\n{address_C}")

print("✅ Task Complete!\n")