# VGS (Very Good Security)

PCI DSS compliance has 300+ controls. The average company spends 6-12 months and six figures achieving it. VGS lets you skip almost all of that by ensuring sensitive data never touches your servers in the first place.

## What it does

VGS operates a data security vault that sits between your application and the outside world. When sensitive data — credit card numbers, SSNs, bank account details, health records — flows through your system, VGS intercepts it, stores the real value in their vault, and hands you back a token. Your application works with tokens everywhere. When you need to send the real data downstream (to a payment processor, for example), VGS swaps the token back to the real value on the way out.

You never see, store, or transmit the sensitive data. It passes through your infrastructure as an opaque reference.

## How it works

The architecture is proxy-based. VGS provides inbound and outbound reverse proxies that you route traffic through. On the inbound side (data coming into your app), VGS redacts sensitive fields and replaces them with tokens before the request reaches your server. On the outbound side (data going to third parties), VGS reveals the tokens back to real values before forwarding the request.

Configuration is done through a dashboard where you define routes and transformation rules — which fields to tokenize, what format the tokens should take (you can preserve format, so a tokenized card number still looks like a card number), and where to apply the transformations.

The vault itself is SOC 2 Type 2 and PCI DSS Level 1 certified. By using VGS, your own PCI scope shrinks dramatically because cardholder data never enters your environment.

## Where it fits in the agent economy

Agents that facilitate purchases, process payments, or handle any form of PII on behalf of users face immediate compliance questions. If an agent collects a credit card number to make a purchase, that agent's infrastructure is now in PCI scope. If it handles health data, HIPAA applies.

VGS provides a way to build payment-capable agents without taking on the compliance burden directly. An agent can collect payment information from a user, pass it through VGS to get a token, and operate entirely on tokens from that point forward. The real card data lives in VGS's vault, not in the agent's memory or logs.

For multi-agent systems where data flows between services, tokenization also limits blast radius. If one agent is compromised, the attacker gets tokens, not real data.

## Limitations

VGS adds latency. Every request that needs tokenization or detokenization makes a round trip through their proxy. For high-frequency, low-latency applications, this overhead matters.

The proxy-based model works well for HTTP traffic but is less natural for non-HTTP protocols, streaming data, or batch processing pipelines. You may need to restructure how data flows through your system.

Debugging can be harder when the data you see in your logs and databases is tokenized. VGS provides tools for this, but it is an adjustment.

Pricing is volume-based and not publicly listed. For startups processing low volumes, costs are reasonable. At scale, it is worth doing the math against building your own vault.

**Links:** [vgs.io](https://www.verygoodsecurity.com/) | [Docs](https://www.verygoodsecurity.com/docs/)
