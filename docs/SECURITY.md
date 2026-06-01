# Noema Core — Security Review Checklist (Phase 03)

> Public proof over promises. Testnet first.  
> ⚠️ Do not use with mainnet funds before external audit.

---

## 🎯 Goal

This checklist ensures Noema Core contracts, SDK and infrastructure meet security standards before mainnet deployment.

---

## ✅ Phase 01-02: Completed (Testnet)

- [x] Contracts deployed on Base Sepolia
- [x] Source code verified on BaseScan
- [x] Foundry tests passing (`forge test`)
- [x] Python SDK functional (`demo_agent.py`)
- [x] GitHub repo public + CI/CD (GitHub Actions)
- [x] API docs + whitepaper published

---

## 🔄 Phase 03: Security Review (In Progress)

### 🔍 Static Analysis
- [ ] Run `slither .` on `smart_contracts/` — zero high/critical findings
- [ ] Run `solhint` — enforce Solidity style guide
- [ ] Check for reentrancy, overflow, access control, timestamp dependence

### 🧪 Formal Verification / Invariants
- [ ] Define Foundry invariants for:
  - Escrow: funds cannot be released without consumer/provider agreement OR dispute resolution
  - Trust: reputation score ∈ [0, 1], slashing only on verified SLA failure
  - Token: total supply fixed, no mint/burn after deployment
- [ ] Run `forge invariant` tests

### 👥 External Audit Scope
- [ ] Prepare audit brief:
  - Contracts: `NoemaToken.sol`, `EscrowLayer.sol`, `TrustLayer.sol`, `RoutingLayer.sol`
  - Key functions: `openEscrow()`, `settle()`, `dispute()`, `slashProvider()`
  - Threat model: malicious provider, replay attacks, griefing, oracle manipulation
- [ ] Engage reputable auditor (e.g., OpenZeppelin, Trail of Bits, Spearbit)
- [ ] Publish audit report + remediation status

### 🐍 SDK Security
- [ ] Review `noema_sdk.py` for:
  - Private key handling (never log, use `.env`, support hardware wallets)
  - Signature verification (ECDSA, replay protection via nonce/timestamp)
  - RPC endpoint validation (prevent MITM)
- [ ] Add integration tests: mock provider, simulate dispute flow

### 🕵️ Bug Bounty Prep
- [ ] Define scope: contracts + SDK + gateway
- [ ] Set reward tiers (e.g., $500–$5000 based on severity)
- [ ] Choose platform (Immunefi, HackerOne) or self-hosted program
- [ ] Publish `SECURITY.md` with reporting guidelines

---

## ⏳ Phase 04: Pre-Mainnet Gates

- [ ] All Phase 03 items completed + documented
- [ ] Audit report published + critical/high issues resolved
- [ ] Bug bounty program live
- [ ] Legal review of token utility + disclaimer language
- [ ] Community governance proposal for mainnet upgrade (if applicable)

---

## 📬 Reporting a Vulnerability

If you find a security issue in Noema Core:

1. **Do not** disclose publicly until coordinated fix
2. Email: `noema.core@proton.me` with subject `[SECURITY]`
3. Include: affected component, reproduction steps, impact assessment
4. We will respond within 48 hours with next steps

---

*Built for agents. Proven by transactions.*  
© 2026 Noema Core. MIT License.
