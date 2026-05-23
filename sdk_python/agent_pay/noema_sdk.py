import os
import json
from web3 import Web3
from dotenv import load_dotenv
from pathlib import Path

class NoemaAgent:
    def __init__(self):
        # 1. Inteligentne ładowanie zmiennych środowiskowych z pliku .env
        env_path = Path(__file__).resolve().parent.parent.parent / 'smart_contracts' / '.env'
        load_dotenv(dotenv_path=env_path)
        
        # 2. Połączenie z blockchainem
        rpc_url = os.getenv('RPC_URL')
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError("Nie można połączyć się z węzłem RPC (Anvil).")
            
        # 3. Konfiguracja portfela Agenta
        self.private_key = os.getenv('PRIVATE_KEY')
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.address = self.account.address
        
        # 4. Adresy kontraktów
        self.token_address = Web3.to_checksum_address(os.getenv('NOEMA_TOKEN_ADDRESS'))
        self.trust_address = Web3.to_checksum_address(os.getenv('TRUST_LAYER_ADDRESS'))
        
        # 5. Minimalne ABI (Interfejsy potrzebne do rozmowy z kontraktami)
        token_abi = json.loads('[{"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]')
        trust_abi = json.loads('[{"inputs":[{"name":"amount","type":"uint256"}],"name":"stake","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"","type":"address"}],"name":"isVerified","outputs":[{"name":"","type":"bool"}],"stateMutability":"view","type":"function"}]')
        
        # 6. Inicjalizacja obiektów kontraktów
        self.token_contract = self.w3.eth.contract(address=self.token_address, abi=token_abi)
        self.trust_contract = self.w3.eth.contract(address=self.trust_address, abi=trust_abi)
        
        print(f"🤖 Agent Noema zainicjalizowany. Adres: {self.address}")

    def is_verified(self):
        """Sprawdza status weryfikacji w TrustLayer (tylko odczyt, bez gazu)."""
        return self.trust_contract.functions.isVerified(self.address).call()

    def join_swarm(self, amount_in_tokens=100):
        """Zatwierdza tokeny i wykonuje staking, aby dołączyć do Roju."""
        amount_wei = self.w3.to_wei(amount_in_tokens, 'ether')
        nonce = self.w3.eth.get_transaction_count(self.address)
        
        print(f"🔄 Rozpoczynam proces onboardingu (Staking {amount_in_tokens} $NOEMA)...")
        
        # Krok A: Approve (Zezwolenie na pobranie tokenów)
        approve_txn = self.token_contract.functions.approve(self.trust_address, amount_wei).build_transaction({
            'chainId': self.w3.eth.chain_id,
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
        })
        signed_approve = self.w3.eth.account.sign_transaction(approve_txn, self.private_key)
        tx_hash_approve = self.w3.eth.send_raw_transaction(signed_approve.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash_approve)
        print(f"✅ Approve zakończone. TX: {tx_hash_approve.hex()}")
        
        # Krok B: Stake (Faktyczne zamrożenie tokenów)
        nonce += 1
        stake_txn = self.trust_contract.functions.stake(amount_wei).build_transaction({
            'chainId': self.w3.eth.chain_id,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
        })
        signed_stake = self.w3.eth.account.sign_transaction(stake_txn, self.private_key)
        tx_hash_stake = self.w3.eth.send_raw_transaction(signed_stake.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash_stake)
        print(f"✅ Stake zakończone. TX: {tx_hash_stake.hex()}")
        
        return self.is_verified()
