# Exa

Most search engines return ten blue links and expect a human to click through them. Exa returns structured content and expects a machine to process it. That distinction defines everything about the product.

## What it does

Exa is a neural search engine built for AI consumption. Originally founded as Metaphor, the company rebranded to Exa to reflect its evolution from a research project into production search infrastructure for AI agents.

The core offering is an API with two primary endpoints: `/search` and `/contents`. The search endpoint accepts natural language queries and returns ranked results using embeddings-based retrieval rather than keyword matching. The contents endpoint takes URLs and returns clean, structured text extracted from web pages — no HTML tags, no navigation chrome, no cookie banners. Just the content.

The difference between embeddings-based search and keyword search matters for agents. A keyword search for "companies building AI payment infrastructure" requires you to guess the exact terms a page uses. An embeddings-based search understands the semantic intent: it will find pages about "agent billing protocols" or "machine-to-machine transaction platforms" even if they never use the phrase "AI payment infrastructure."

## How it works

Exa maintains its own web index, built by crawling and embedding web content into a high-dimensional vector space. When a query comes in, Exa embeds the query into the same vector space and finds the nearest neighbors — pages whose content is semantically similar to the query's meaning, not just its keywords.

The API is straightforward:

```python
from exa_py import Exa

exa = Exa(api_key="your-key")

# Semantic search
results = exa.search(
    "startups building payment infrastructure for AI agents",
    num_results=10,
    type="neural"
)

# Get clean content from results
contents = exa.get_contents(
    [r.url for r in results.results],
    text=True
)
```

The search endpoint supports filters for domain, date range, and content type. You can restrict results to specific sites, exclude domains, or limit to content published within a time window. The `type` parameter lets you choose between `neural` (semantic) and `keyword` (traditional) search, or `auto` to let Exa decide.

The contents endpoint is where Exa diverges most from traditional search. Instead of returning snippets, it extracts the full text content from each page in a clean, structured format. For an AI agent, this eliminates the entire scraping-and-parsing pipeline that would otherwise be required to go from search results to usable information.

Results include metadata: URL, title, published date, author (when available), and a relevance score. The structured output is designed to be fed directly into an LLM context window without preprocessing.

## Where it fits in the agent economy

Every agent that needs to know something about the world outside its training data needs search. Research agents, competitive intelligence agents, news monitoring agents, due diligence agents — they all share the same fundamental need: find relevant information and extract usable content from it.

In our hackathon economy, Exa is the knowledge layer. The Architect uses search capabilities to gather information for its orchestration pipeline. The Oracle uses web data to enrich marketplace intelligence. Any agent that answers questions beyond its training cutoff needs a search provider, and Exa is purpose-built for that use case.

The semantic search capability is particularly valuable for agent-to-agent discovery. An agent looking for "services that verify the quality of AI-generated content" can find The Gold Star through Exa even if The Gold Star's description never uses those exact words. This is how organic discovery works in an agent economy — through semantic search that understands intent rather than a centralized registry.

The clean content extraction eliminates an entire class of agent infrastructure — web scrapers, HTML parsers, boilerplate strippers — replacing it with a single API call.

## Limitations

Exa's index is smaller than Google's. For obscure topics, niche technical documentation, or recently published content, coverage gaps exist. The index favors English-language content and well-known domains. Deep web content, paywalled articles, and dynamically rendered single-page applications may be missing or poorly indexed.

The API is rate-limited with tiered pricing. High-volume agents that need thousands of searches per hour will hit rate limits on lower tiers. Cost can scale quickly for research-intensive agents that make many queries per task.

Semantic search is not always better than keyword search. For precise technical queries — error messages, exact function names, specific version numbers — keyword matching outperforms embeddings-based retrieval. Exa offers both modes, but the neural mode is the default, and it can return tangentially related results when precision is needed.

The contents endpoint depends on being able to fetch and parse the target URL at request time. Pages behind authentication, heavy JavaScript rendering, or takedowns since indexing will return incomplete or empty results.

Despite these constraints, Exa fills a genuine gap. Search infrastructure designed for machines rather than humans is exactly what the agent economy needs, and Exa is the clearest execution of that idea currently available.
