import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException  # type: ignore
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RPC_USER = os.getenv("RPC_USER")
RPC_PASSWORD = os.getenv("RPC_PASSWORD")
RPC_PORT = os.getenv("RPC_PORT")
WALLET_NAME = os.getenv("WALLET_NAME")

RPC_URL = f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:{RPC_PORT}"

rpc_connection = AuthServiceProxy(RPC_URL)
wallet_rpc = AuthServiceProxy(f"{RPC_URL}/wallet/{WALLET_NAME}")

# Fetch addresses
with open("./addresses.txt", "r") as f:
    address_A, address_B, address_C = [line.strip() for line in f.readlines()]

print("\n🔎 Fetching UTXOs for Address B...")
utxos = wallet_rpc.listunspent()
utxo_B = next((utxo for utxo in utxos if utxo['address'] == address_B and utxo['spendable']), None)

if not utxo_B:
    raise Exception(f"No spendable UTXO found for Address B ({address_B}).")

print(f"✅ UTXO found for Address B:\n  Address: {address_B}\n  TxID: {utxo_B['txid']}\n  Amount: {utxo_B['amount']:.8f} BTC\n")

# Create Transaction from B to C
print("\n💸 Creating Transaction from B to C...")
FEE = Decimal('0.00001')
send_amount = Decimal('0.05').quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
change = Decimal(utxo_B['amount']) - send_amount - FEE

if change <= Decimal('0.00000546'):
    raise ValueError("Change amount is non-positive — reduce send amount or increase UTXO.")

inputs = [{
    "txid": utxo_B['txid'],
    "vout": utxo_B['vout']
}]

outputs = {
    address_C: float(send_amount),
    address_B: float(change)
}

raw_tx = wallet_rpc.createrawtransaction(inputs, outputs)
print(f"✅ Raw Transaction Created: {raw_tx}\n")

# Sign and Broadcast Transaction
signed_tx = wallet_rpc.signrawtransactionwithwallet(raw_tx)
if not signed_tx.get('complete'):
    raise Exception("Transaction signing failed.")

print(f"✅ Transaction Signed: {signed_tx['hex']}\n")

txid = wallet_rpc.sendrawtransaction(signed_tx['hex'])
print(f"✅ Transaction Broadcasted! TxID: {txid}\n")

# Decode and Analyze Transaction
print("\n🔎 Decoding Transaction...")
decoded_tx = wallet_rpc.decoderawtransaction(signed_tx['hex'])

# Show full decoded transaction
print(f"✅ Decoded Transaction: {decoded_tx}\n")

# Extract and compare scripts
for vin in decoded_tx['vin']:
    print(f"🔒 ScriptSig (Unlocking Script): {vin['scriptSig']['asm']}")
    print(f"ScriptSig (Hex): {vin['scriptSig']['hex']}\n")

for vout in decoded_tx['vout']:
    if vout['scriptPubKey']['address'] == address_C:
        print(f"🔑 ScriptPubKey (Locking Script) for Address C: {vout['scriptPubKey']['asm']}")
        print(f"ScriptPubKey (Hex): {vout['scriptPubKey']['hex']}\n")

# Final Wallet Balance
balance = wallet_rpc.getbalance()
print(f"💰 Final Wallet Balance: {balance:.8f} BTC\n")

# Mine a block to confirm the transaction
miner_address = wallet_rpc.getnewaddress("", "legacy")
block_hash = rpc_connection.generatetoaddress(1, miner_address)
print(f"✅ Block mined: {block_hash[0]}\n")

# Save addresses
with open("addresses.txt", "w") as f:
    f.write(f"{address_A}\n{address_B}\n{address_C}")

print("✅ Task Complete!\n")
