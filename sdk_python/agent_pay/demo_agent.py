from noema_sdk import NoemaAgent
from web3 import Web3

def main():
    print("="*50)
    print("🤖 NOEMA CORE — PUBLIC DEMO (Sepolia)")
    print("="*50)
    
    # 1. Inicjalizacja Agenta
    agent = NoemaAgent()
    
    # 2. Pokaż podstawowe dane
    chain_id = agent.w3.eth.chain_id
    balance_wei = agent.w3.eth.get_balance(agent.address)
    balance_eth = agent.w3.from_wei(balance_wei, "ether")
    
    print(f"\n🌐 Sieć: Sepolia (Chain ID: {chain_id})")
    print(f"🤖 Adres Agenta: {agent.address}")
    print(f"💰 Saldo ETH: {balance_eth:.4f}")
    
    # 3. Pokaż dane tokena
    token_name = agent.token_contract.functions.name().call()
    print(f"🪙 Token: {token_name}")
    
    # 4. Pokaż adresy kontraktów (public proof)
    print(f"\n🔗 EscrowLayer: {agent.escrow_contract.address}")
    print(f"🔗 TrustLayer: {agent.trust_address}")
    
    print("\n✅ Stack działa end-to-end na publicznym Sepolia!")
    print("="*50)

if __name__ == "__main__":
    main()
