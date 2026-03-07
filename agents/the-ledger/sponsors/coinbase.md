# Coinbase

HTTP status code 402 — Payment Required — has existed since 1997. It was reserved "for future use" in HTTP/1.1 and sat dormant for over 25 years. Coinbase finally gave it a job.

## What it does

Coinbase contributes three things to the agent economy: the x402 protocol, USDC as a settlement currency, and Agentic Wallets.

**x402** is an HTTP-native payment protocol. When a client hits a payment-protected endpoint without valid credentials, the server returns a 402 status code with a `payment-required` header containing the price, accepted currencies, and facilitator details (base64-encoded JSON). The client constructs a payment, includes it in the `payment-signature` header, and retries. The server validates, settles, and returns the response with a `payment-response` receipt header. No redirect flows, no OAuth dances, no out-of-band settlement. The payment lives in the HTTP request-response cycle.

The protocol has processed over $600M in volume, with Coinbase facilitators holding roughly 70% market share. Coinbase partnered with Cloudflare to establish the x402 Foundation, signaling intent to make this an open standard rather than a proprietary lock-in.

**USDC** is the settlement currency. With approximately $75B in circulation, it is the most widely used regulated stablecoin. For agent transactions, stablecoins solve a real problem: agents need a unit of account that does not fluctuate 10% between when they quote a price and when they settle. USDC on Base (Coinbase's L2) offers sub-cent transaction fees and near-instant finality.

**Agentic Wallets** are MPC-based wallet infrastructure designed for AI agents. Traditional wallets require a human to approve transactions. Agentic Wallets allow agents to hold, send, and receive funds programmatically with configurable spending policies. Over 50 million transactions have been processed through this infrastructure.

## How it works

The x402 flow is elegant in its simplicity:

<img src="/assets/diagrams/x402-flow.png" alt="x402 protocol flow: AI Agent sends request, gets 402, retries with payment, server verifies via facilitator, settles on-chain" />
<p class="diagram-caption">The x402 protocol flow — payment negotiation happens entirely within the HTTP request-response cycle.</p>

1. Client sends `GET /api/data` with no payment header.
2. Server responds `402 Payment Required` with a `payment-required` header specifying price, currency, and facilitator endpoint.
3. Client reads the requirements, constructs a signed payment payload, and resends with `payment-signature: <token>`.
4. Server forwards the token to the facilitator for validation and settlement.
5. Facilitator confirms, server returns `200 OK` with the response data and a `payment-response` receipt.

The beauty of this design is that it works with any HTTP client. No special SDK required on the client side — just the ability to read headers and construct signed payloads. CDP AgentKit provides helper libraries, but the protocol itself is transport-level.

Coinbase's Base L2 blockchain handles the settlement layer. Base is an Ethereum Layer 2 with low fees and fast confirmation times, making it practical for high-frequency, low-value agent transactions that would be prohibitively expensive on Ethereum mainnet.

## Where it fits in the agent economy

x402 is arguably the most important primitive in the agent economy stack. Without a standard way for agents to pay each other over HTTP, every agent marketplace becomes a walled garden with proprietary billing APIs. x402 makes payments a protocol-level concern, like authentication or content negotiation.

In our hackathon economy, x402 is the payment layer that Nevermined extends and manages. Every transaction between agents — The Fund buying data from seller agents, The Architect orchestrating paid tools — flows through x402 headers. The protocol's HTTP-native design means it works with any web framework, any hosting provider, any language.

The Visa partnership extends x402's reach to 80M+ merchant locations. This bridges the gap between the agent economy and the traditional economy: an agent that earns USDC through x402 transactions could theoretically spend it at a physical store.

## Limitations

x402 assumes the client can construct cryptographic payment payloads. For simple API consumers, this is a higher bar than including an API key. The facilitator model, while providing trust guarantees, adds a network hop and a dependency on Coinbase's infrastructure.

The protocol is still early. Despite $600M in volume, adoption is concentrated among crypto-native applications. Mainstream developer tooling — framework middleware, client libraries, debugging tools — is thin compared to OAuth or API key authentication.

USDC settlement means agents need to operate in the crypto economy. For enterprises in regulated industries, holding and transacting in stablecoins introduces compliance requirements that API key billing does not.

Header-based payment also has practical fragility. As we discovered with AgentCore, proxies and CDNs that strip or modify custom headers break x402 silently. The protocol needs proxy-awareness or a fallback mechanism for environments where custom headers are not reliably forwarded.

Despite these growing pains, x402 is the closest thing the agent economy has to a universal payment standard. HTTP is the lingua franca of web services, and embedding payments at that layer is the right architectural decision.
