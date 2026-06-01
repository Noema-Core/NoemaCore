from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja
RPC_URL = os.getenv("RPC_URL", "https://sepolia.base.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ROUTER_ADDRESS = os.getenv("ROUTER_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL)) if RPC_URL else None

# Minimalny ABI dla SandboxRouter.submitAttestation
ROUTER_ABI = [{
    "inputs": [
        {"name": "_executionId", "type": "bytes32"},
        {"name": "_attestationHash", "type": "bytes32"}
    ],
    "name": "submitAttestation",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}]

def _get_router():
    """Leniwa inicjalizacja kontraktu — tylko gdy potrzebny."""
    if not PRIVATE_KEY or not ROUTER_ADDRESS:
        raise ValueError("Missing PRIVATE_KEY or ROUTER_ADDRESS in .env")
    if not w3 or not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {RPC_URL}")
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    router = w3.eth.contract(
        address=Web3.to_checksum_address(ROUTER_ADDRESS),
        abi=ROUTER_ABI
    )
    return router, account

def submit_attestation(execution_id_hex: str, attestation_hash_hex: str) -> bool:
    """Wysyła dowód wykonania z sandboxa do kontraktu SandboxRouter."""
    try:
        router, account = _get_router()
        
        tx = router.functions.submitAttestation(
            bytes.fromhex(execution_id_hex.replace("0x", "")),
            bytes.fromhex(attestation_hash_hex.replace("0x", ""))
        ).build_transaction({
            "from": account.address,
            "gas": 150_000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": w3.eth.chain_id
        })
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.status == 1
    except Exception as e:
        print(f"[!] Web3 submission error: {e}")
        return False
