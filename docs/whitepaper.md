# Noema Core — Technical Whitepaper (Draft)

> Public proof over promises. Testnet first.  
> Chain: Base Sepolia (Chain ID: 84532) • Contracts verified on BaseScan

---

## 🎯 Mission

Noema Core is an EVM protocol where AI agents can:
- 🔍 Discover compute/providers via on-chain routing
- 🔒 Lock funds in escrow before work begins
- ⚡ Consume compute off-chain via signed usage frames
- ⚖️ Settle on-chain with reputation updates and slashing

**Not an app. Infrastructure for agent commerce.**

---

## 🏗️ Four-Layer Architecture

### 🪙 Layer 1: Token ($NOEMA)
- Fixed supply, EVM-native
- Used for: staking, collateral, fee accounting, settlement
- **Why not stablecoins?** Native collateral binds reputation risk + protocol fees + dispute penalties into one mechanism

### 🔒 Layer 2: Escrow
- Funds locked **before** work starts
- Supports: release, refund, dispute paths
- State channels aggregate 1000s of off-chain events → 1 on-chain settlement

### 🛡️ Layer 3: Trust & Slashing
- Stake-backed provider accountability
- Objective SLA metrics: timeout, availability, signed usage proofs
- Automatic slashing for verifiable failures

### ⚡ Layer 4: Routing & Channels
- Off-chain usage frames (signed by consumer)
- Aggregation layer: batch micro-calls → efficient settlement
- Provider selection via reputation score + capacity signals

---

## 🔐 Security Philosophy

1. **Testnet first** — public proof before mainnet promises
2. **Verified contracts** — source code public on BaseScan
3. **No APY claims** — utility before speculation
4. **External audit required** — before any mainnet liquidity

---

## 🗺️ Roadmap (Conservative, Verifiable)

| Phase | Goal | Deliverable |
|-------|------|-------------|
| **01** ✅ | Sepolia deployment | Contracts live, verified, SDK working |
| **02** ✅ | GitHub + docs | Open repo, README, API reference |
| **03** 🔄 | Security review | Slither, Foundry invariants, external audit |
| **04** ⏳ | Provider sandbox | Early devs stress-test routing + settlement |

---

## ⚠️ Disclaimer

> This document describes testnet software. No mainnet promises before external audit, legal review, and community governance.  
> $NOEMA is a protocol utility token, not an investment vehicle.

*Built for agents. Proven by transactions.*  
© 2026 Noema Core. MIT License.
