import os
from web3 import Web3

print("🤖 Inicjalizacja Agenta Noema Grid...")

# Proste ładowanie zmiennych z pliku .env (bez dodatkowych bibliotek)
env_path = '../../smart_contracts/.env'
with open(env_path, 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# 1. Połączenie z lokalnym blockchainem (Anvil)
rpc_url = os.environ.get('RPC_URL')
w3 = Web3(Web3.HTTPProvider(rpc_url))

if w3.is_connected():
    print("✅ Połączono z prywatnym blockchainem (Anvil)!")
else:
    print("❌ Błąd połączenia z RPC.")
    exit()

# 2. Adresy
TRUST_LAYER_ADDRESS = Web3.to_checksum_address(os.environ.get('TRUST_LAYER_ADDRESS'))
MY_ADDRESS = Web3.to_checksum_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")

# 3. Fragment ABI (interfejs) potrzebny do odczytu funkcji isVerified
TRUST_ABI = '[{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"isVerified","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}]'

# 4. Inicjalizacja kontraktu
trust_contract = w3.eth.contract(address=TRUST_LAYER_ADDRESS, abi=TRUST_ABI)

# 5. Odczyt statusu z blockchaina
is_verified = trust_contract.functions.isVerified(MY_ADDRESS).call()

print("-" * 40)
print(f"Portfel: {MY_ADDRESS}")
print(f"Status weryfikacji (isVerified): {is_verified}")
if is_verified:
    print("🎉 Agent AI jest oficjalnie zweryfikowanym węzłem w Roju Noema Grid!")
else:
    print("⚠️ Agent nie posiada statusu weryfikacji.")
