# Privy

Every web3 application has the same onboarding problem: you need users to have a wallet before they can do anything, but asking someone to install MetaMask and write down a seed phrase is a 90% drop-off event. Privy makes wallets invisible.

## What it does

Privy is an authentication and embedded wallet provider for web3 applications — significant enough that Stripe acquired them in June 2025 to expand its web3 capabilities. When a user signs in — via email, phone number, Google, Twitter, Discord, or any supported social login — Privy creates a non-custodial MPC (multi-party computation) wallet behind the scenes. The user never sees a seed phrase, never installs an extension, never knows they have a wallet at all. They just log in and start using the app.

The wallet is real. It can hold tokens, sign transactions, interact with smart contracts. But the complexity is abstracted away entirely.

## How it works

Privy uses MPC key sharding to split private keys across multiple parties. No single entity — not Privy, not the app developer, not the user — holds the complete key. This means Privy cannot unilaterally access user funds, which matters for trust.

The integration is SDK-based. You drop in `@privy-io/react-auth` (or the relevant SDK for your stack), configure your auth methods, and Privy handles the rest: session management, wallet creation, transaction signing. There are also server wallets for programmatic use cases — backend services that need to sign transactions without user interaction.

The progressive security model is worth noting. Users start with a simple login, then can optionally add additional authentication factors or export their keys if they want full self-custody later. This is a pragmatic middle ground between "not your keys, not your coins" purists and the reality that most people will never manage a private key.

## Where it fits in the agent economy

Agents need identity and they need wallets. An autonomous agent that discovers a service, negotiates a price, and pays for it needs a way to hold funds and authorize transactions. Privy's server wallets are directly relevant here — they provide programmatic signing without requiring a human in the loop for every transaction.

In the agent economy context, Privy could serve as the identity layer: each agent gets a wallet on creation, can accumulate earnings, make payments, and build on-chain history. The embedded wallet model means spinning up a new agent does not require manual key management.

For human users interacting with the agent economy through a frontend, Privy removes the friction of connecting a wallet just to buy credits or subscribe to an agent's service.

## Limitations

Privy is a hosted service. Your authentication flow depends on Privy's infrastructure being available. For applications that need to function fully offline or in air-gapped environments, this is a non-starter.

MPC wallets, while secure, are not identical to traditional self-custody. Users who want full control from day one may find the progressive disclosure model frustrating. Key export is available, but it is not the default path.

Pricing is usage-based and can scale up quickly for high-volume applications. The free tier is generous for prototyping, but production costs should be evaluated early.

Finally, Privy is primarily EVM-focused. If your agent economy spans non-EVM chains, you will need additional infrastructure for those environments.

**Links:** [privy.io](https://www.privy.io/) | [Docs](https://docs.privy.io/)
