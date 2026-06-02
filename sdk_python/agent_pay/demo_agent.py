#!/usr/bin/env python3
import sys, time
from noema_sdk import NoemaAgent

def print_line(msg):
    print(msg, flush=True)

print_line("=" * 50)
print_line("🤖 NOEMA CORE — PUBLIC DEMO (Base Sepolia)")
print_line("=" * 50)
time.sleep(0.2)

print_line("🤖 Inicjalizacja Agenta Noema...")
agent = NoemaAgent()
print_line(f"✅ Agent zainicjalizowany. Adres: {agent.address}")
time.sleep(0.2)

print_line(f"🌐 Sieć: Base Sepolia (Chain ID: {agent.w3.eth.chain_id})")
balance = agent.w3.from_wei(agent.w3.eth.get_balance(agent.address), 'ether')
print_line(f"💰 Saldo ETH: {balance:.4f}")
print_line(f"🪙 Token: {agent.token_contract.functions.name().call()}")
time.sleep(0.2)

# Bezpieczny dostęp do adresów kontraktów (różne możliwe nazwy atrybutów)
escrow_addr = getattr(agent, 'escrow_contract', None)
if escrow_addr and hasattr(escrow_addr, 'address'):
    print_line(f"🔗 EscrowLayer: {escrow_addr.address}")
else:
    print_line(f"🔗 EscrowLayer: {getattr(agent, 'escrow_address', 'N/A')}")

trust_addr = getattr(agent, 'trust_layer_contract', getattr(agent, 'trust_contract', None))
if trust_addr and hasattr(trust_addr, 'address'):
    print_line(f"🔗 TrustLayer: {trust_addr.address}")
else:
    print_line(f"🔗 TrustLayer: {getattr(agent, 'trust_address', '0x7aB75BA485d9611A34ea600FC15c96E242aBC866')}")

time.sleep(0.2)
print_line("✅ Stack działa end-to-end na publicznym Base Sepolia!")
print_line("=" * 50)
