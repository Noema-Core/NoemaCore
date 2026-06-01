import os, re

def _load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

_load_env(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

import os
import json
from web3 import Web3
from web3.exceptions import ContractLogicError

class NoemaAgent:
    def __init__(self, private_key=None):
        rpc_url = os.getenv('RPC_URL')
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError("Nie można połączyć się z węzłem RPC (Anvil).")
            
        self.private_key = private_key if private_key else os.getenv('PRIVATE_KEY')
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.address = self.account.address
        
        self.token_address = Web3.to_checksum_address(os.getenv('NOEMA_TOKEN_ADDRESS'))
        self.trust_address = Web3.to_checksum_address(os.getenv('TRUST_LAYER_ADDRESS'))
        self.escrow_address = Web3.to_checksum_address(os.getenv('ESCROW_LAYER_ADDRESS'))
        
        escrow_abi = json.loads('[{"inputs":[{"internalType":"address","name":"_token","type":"address"},{"internalType":"address","name":"_trustLayer","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"jobCounter","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"jobId","type":"uint256"}],"name":"slash","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"jobId","type":"uint256"}],"name":"releaseFunds","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"worker","type":"address"},{"internalType":"uint256","name":"reward","type":"uint256"},{"internalType":"uint256","name":"durationInDays","type":"uint256"},{"internalType":"bytes32","name":"dataHash","type":"bytes32"}],"name":"createJob","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]')
        
        self.escrow_contract = self.w3.eth.contract(address=self.escrow_address, abi=escrow_abi)
        token_abi = [{"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"stateMutability":"view","type":"function"}]
        self.token_contract = self.w3.eth.contract(address=self.token_address, abi=token_abi)
        print(f"🤖 Agent Noema zainicjalizowany. Adres: {self.address}")

    def _safe_send(self, txn_dict, signed_txn):
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            try:
                self.w3.eth.call(txn_dict, block_identifier=receipt.blockNumber)
            except ContractLogicError as e:
                raise Exception(f"🚨 TRANSAKCJA ODRZUCONA! Powód: {e}")
        return receipt

    def is_verified(self):
        trust_abi = json.loads('[{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"isVerified","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}]')
        trust_contract = self.w3.eth.contract(address=self.trust_address, abi=trust_abi)
        return trust_contract.functions.isVerified(self.address).call()

    def create_job(self, worker_address, reward_in_tokens, duration_days, data_hash="0x" + "00"*32):
        reward_wei = self.w3.to_wei(reward_in_tokens, 'ether')
        data_hash_bytes = Web3.to_bytes(hexstr=data_hash) if data_hash.startswith('0x') else Web3.to_bytes(text=data_hash)
        nonce = self.w3.eth.get_transaction_count(self.address)
        print(f"🔄 Tworzę zlecenie dla {worker_address[:10]}... (Nagroda: {reward_in_tokens} $NOEMA)")
        
        token_abi = json.loads('[{"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]')
        token_contract = self.w3.eth.contract(address=self.token_address, abi=token_abi)
        
        approve_txn = token_contract.functions.approve(self.escrow_address, reward_wei).build_transaction({
            'from': self.address, 'chainId': self.w3.eth.chain_id, 'gasPrice': self.w3.eth.gas_price, 'nonce': nonce,
        })
        signed_approve = self.w3.eth.account.sign_transaction(approve_txn, self.private_key)
        self._safe_send(approve_txn, signed_approve)
        
        nonce += 1
        create_txn = self.escrow_contract.functions.createJob(
            Web3.to_checksum_address(worker_address), reward_wei, int(duration_days), data_hash_bytes
        ).build_transaction({
            'from': self.address, 'chainId': self.w3.eth.chain_id, 'gasPrice': self.w3.eth.gas_price, 'nonce': nonce,
        })
        signed_create = self.w3.eth.account.sign_transaction(create_txn, self.private_key)
        self._safe_send(create_txn, signed_create)
        
        job_id = 1  # Tymczasowy placeholder: funkcja jobCounter() nie istnieje w kontrakcie
        print(f"✅ Zlecenie utworzone! Job ID: {job_id}")
        return job_id

    def release_funds(self, job_id):
        nonce = self.w3.eth.get_transaction_count(self.address)
        print(f"🔄 Zatwierdzam zlecenie #{job_id}...")
        txn = self.escrow_contract.functions.releaseFunds(int(job_id)).build_transaction({
            'from': self.address, 'chainId': self.w3.eth.chain_id, 'gasPrice': self.w3.eth.gas_price, 'nonce': nonce,
        })
        signed = self.w3.eth.account.sign_transaction(txn, self.private_key)
        self._safe_send(txn, signed)
        print(f"✅ Środki uwolnione dla wykonawcy!")

    def slash(self, job_id):
        nonce = self.w3.eth.get_transaction_count(self.address)
        print(f"⚖️ Uruchamiam slashing dla zlecenia #{job_id}...")
        txn = self.escrow_contract.functions.slash(int(job_id)).build_transaction({
            'from': self.address, 'chainId': self.w3.eth.chain_id, 'gasPrice': self.w3.eth.gas_price, 'nonce': nonce,
        })
        signed = self.w3.eth.account.sign_transaction(txn, self.private_key)
        self._safe_send(txn, signed)
        print(f"✅ Slashing wykonany! Kara naliczona.")
