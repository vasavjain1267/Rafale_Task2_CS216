# 🚀 Bitcoin Scripts in Regtest Mode - README

## 📌 Introduction
This guide provides a step-by-step approach to running Bitcoin scripts in Regtest mode using Bitcoin Core. You'll learn how to install Bitcoin Core, configure it for Regtest mode, generate test blocks, and run Python scripts to interact with the Bitcoin network.

---

## 🛠 Prerequisites
- macOS with Terminal access
- Python installed
- Bitcoin Core installed
- Basic understanding of Bitcoin transactions

---

## 📂 Project Structure
```
📁 bitcoin_project  
│── 📄 README.md  # This file  
│── 📁 part1  
│   │── 📄 run1.py  # First Python script  
│   │── 📄 run2.py  # Second Python script  
│── 📁 part2  
│   │── 📄 run3.py  # Third Python script  
```

---

## 🔹 Step 1: Install Bitcoin Core
1. Download Bitcoin Core: [Bitcoin Core Download](https://bitcoincore.org/en/download/)  
2. Install it by dragging it to the Applications folder.  
3. Verify the installation:  
   ```bash
   bitcoin-cli --version
   ```

---

## 🔹 Step 2: Configure Bitcoin Core for Regtest Mode
1. Create a Bitcoin data directory:  
   ```bash
   mkdir -p ~/Library/Application\ Support/Bitcoin
   ```
2. Create and edit the configuration file:  
   ```bash
   nano ~/Library/Application\ Support/Bitcoin/bitcoin.conf
   ```
3. Paste the following configuration and save:  
   ```
   regtest=1
   server=1
   txindex=1
   rpcuser=rudrajadon
   rpcpassword=rudra1234
   rpcallowip=127.0.0.1
   rpcport=18443
   fallbackfee=0.0002
   mintxfee=0.00001
   txconfirmtarget=1
   ```

---

## 🔹 Step 3: Start Bitcoin Core in Regtest Mode
Run the following command to start Bitcoin Core:  
```bash
bitcoind -regtest -daemon
```
Verify if it's running:  
```bash
bitcoin-cli -regtest getblockchaininfo
```

---

## 🔹 Step 4: Generate Initial Blocks
Generate 101 blocks to create BTC for testing:  
```bash
bitcoin-cli -regtest generatetoaddress 101 $(bitcoin-cli -regtest getnewaddress)
```

---

## 🔹 Step 5: Run the Part 1 Python Scripts
These scripts:  
✔ Connect to bitcoind  
✔ Create/load a wallet  
✔ Generate 3 legacy addresses (A, B, C)  
✔ Fund address A  
✔ Send BTC from A → B  

Navigate to the **part1** folder and run the scripts:  
```bash
cd /Users/rudrajadon/Desktop/bitcoin_project/part1
python -u run1.py
python -u run2.py
```

If errors occur:  
- Ensure `bitcoind` is running.  
- Check `bitcoin.conf` settings.  
- Create a wallet if necessary:  
  ```bash
  bitcoin-cli -regtest createwallet "test_wallet"
  ```

---

## 🔹 Step 6: Run the Part 2 Python Script
This script:  
✔ Fetches UTXOs from B  
✔ Creates a transaction from B → C  
✔ Decodes & analyzes the transaction  

Navigate to the **part2** folder and run the script:  
```bash
cd /Users/rudrajadon/Desktop/bitcoin_project/part2
python -u run3.py
```

---

## 🔹 Step 7: Debug Bitcoin Scripts
Install `btcdeb` for debugging:  
```bash
brew install bitcoin
```
Or compile from source:  
```bash
git clone https://github.com/bitcoin-core/btcdeb.git
cd btcdeb
make
```

Run the debugger:  
```bash
btcdeb '[OP_DUP OP_HASH160 <pubkeyHash> OP_EQUALVERIFY OP_CHECKSIG]' <sig> <pubkey>
```

---

## 🎯 Summary
✅ **Step 1:** Download & install Bitcoin Core  
✅ **Step 2:** Configure `bitcoin.conf`  
✅ **Step 3:** Start `bitcoind` in Regtest mode  
✅ **Step 4:** Generate test blocks  
✅ **Step 5:** Run `run1.py` and `run2.py` from `part1`  
✅ **Step 6:** Run `run3.py` from `part2`  
✅ **Step 7:** Use `btcdeb` for debugging  

🚀 Now you can run and debug Bitcoin transactions successfully!
