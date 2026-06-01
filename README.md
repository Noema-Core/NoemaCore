# Noema Core 🧠⚡

Decentralized protocol for AI agent coordination, trust verification, and escrow payments.

## 🌐 Public Testnets

### Base Sepolia (Recommended L2)
Contracts live on Base Sepolia — source code verified on BaseScan:

| Contract | Address | BaseScan |
|----------|---------|----------|
| NoemaToken | `0x783A43156954701cfFc55602CDDd0da948E6f249` | [🔍 View](https://sepolia.basescan.org/address/0x783a43156954701cffc55602cddd0da948e6f249#code) |
| TrustLayer | `0x7aB75BA485d9611A34ea600FC15c96E242aBC866` | [🔍 View](https://sepolia.basescan.org/address/0x7ab75ba485d9611a34ea600fc15c96e242abc866#code) |
| EscrowLayer | `0xD5e8fb338b48024E414745217655CB63aB78667f` | [🔍 View](https://sepolia.basescan.org/address/0xd5e8fb338b48024e414745217655cb63ab78667f#code) |
| RoutingLayer | `0x0393CD084BC08FEbe21fA3D541b77559C9590cd4` | [🔍 View](https://sepolia.basescan.org/address/0x0393cd084bc08febe21fa3d541b77559c9590cd4#code) |

### Ethereum Sepolia (Legacy)
| Contract | Address | Etherscan |
|----------|---------|-----------|
| NoemaToken | `0xBddf044D6AF8Ea44fC32Efa3EEeeD5a70152A71e` | [🔍 View](https://sepolia.etherscan.io/address/0xbddf044d6af8ea44fc32efa3eeeed5a70152a71e#code) |
| TrustLayer | `0x027da3d054b3038665B4292D7515946CCA2541F1` | [🔍 View](https://sepolia.etherscan.io/address/0x027da3d054b3038665b4292d7515946cca2541f1#code) |
| EscrowLayer | `0x0061F0E6e8B93c367740B602650f6797164AE704` | [🔍 View](https://sepolia.etherscan.io/address/0x0061f0e6e8b93c367740b602650f6797164ae704#code) |
| RoutingLayer | `0xE8613929e0DEfe73118e445Ed956F03aD8e644ff` | [🔍 View](https://sepolia.etherscan.io/address/0xe8613929e0defe73118e445ed956f03ad8e644ff#code) |

## 🚀 Quick Start
1. Configure `.env` with Base Sepolia RPC: `RPC_URL=https://sepolia.base.org`
2. Deploy: `forge script script/Deploy.s.sol --rpc-url $RPC_URL --private-key $PRIVATE_KEY --broadcast --chain base-sepolia`
3. Test SDK: `cd sdk_python/agent_pay && python3 demo_agent.py`

## 🔐 Security
✅ Contracts verified on BaseScan & Etherscan  
✅ Foundry tests passing  
✅ Local Anvil prototype working  
✅ State channels architecture for micro-usage  

## 💡 Why Base?
- ~100x cheaper than Ethereum Mainnet (~$0.01/tx)
- Full EVM compatibility — same Solidity code
- Fast finality (~2s blocks)
- Coinbase ecosystem integration

## 📦 Repository
GitHub: Coming Soon — open infrastructure for agent commerce.
