[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/cnych-seo-mcp-badge.png)](https://mseep.ai/app/cnych-seo-mcp)

# SEO MCP

A MCP (Model Control Protocol) SEO tool service based on Ahrefs data. Includes features such as backlink analysis, keyword research, traffic estimation, and more.

[中文](./README_CN.md)

## Overview

This service provides an API to retrieve SEO data from Ahrefs. It handles the entire process, including solving the CAPTCHA, authentication, and data retrieval. The results are cached to improve performance and reduce API costs.

> This MCP service is for educational purposes only. Please do not misuse it. This project is inspired by `@哥飞社群`.

## Features

- 🔍 Backlink Analysis

  - Get detailed backlink data for any domain
  - View domain rating, anchor text, and link attributes
  - Filter educational and government domains

- 🎯 Keyword Research

  - Generate keyword ideas from a seed keyword
  - Get keyword difficulty score
  - View search volume and trends

- 📊 Traffic Analysis

  - Estimate website traffic
  - View traffic history and trends
  - Analyze popular pages and country distribution
  - Track keyword rankings

- 🚀 Performance Optimization

  - Use CapSolver to automatically solve CAPTCHA
  - Response caching

## Installation

### Prerequisites

- Python 3.10 or higher
- CapSolver account and API key ([register here](https://dashboard.capsolver.com/passport/register?inviteCode=1dTH7WQSfHD0))

### Install from PyPI

```bash
pip install seo-mcp
```

Or use `uv`:

```bash
uv pip install seo-mcp
```

### Manual Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/cnych/seo-mcp.git
   cd seo-mcp
   ```

2. Install dependencies:

   ```bash
   pip install -e .
   # Or
   uv pip install -e .
   ```

3. Set the CapSolver API key:

   ```bash
   export CAPSOLVER_API_KEY="your-capsolver-api-key"
   ```

## Usage

### Run the service

You can run the service in the following ways:

#### Use in Cursor IDE

In the Cursor settings, switch to the MCP tab, click the `+Add new global MCP server` button, and then input:

```json
{
  "mcpServers": {
    "SEO MCP": {
      "command": "uvx",
      "args": ["--python", "3.10", "seo-mcp"],
      "env": {
        "CAPSOLVER_API_KEY": "CAP-xxxxxx"
      }
    }
  }
}
```

You can also create a `.cursor/mcp.json` file in the project root directory, with the same content.

### API Reference

The service provides the following MCP tools:

#### `get_backlinks_list(domain: str)`

Get the backlinks of a domain.

**Parameters:**

- `domain` (string): The domain to analyze (e.g. "example.com")

**Returns:**

```json
{
  "overview": {
    "domainRating": 76,
    "backlinks": 1500,
    "refDomains": 300
  },
  "backlinks": [
    {
      "anchor": "Example link",
      "domainRating": 76,
      "title": "Page title",
      "urlFrom": "https://referringsite.com/page",
      "urlTo": "https://example.com/page",
      "edu": false,
      "gov": false
    }
  ]
}
```

#### `keyword_generator(keyword: str, country: str = "us", search_engine: str = "Google")`

Generate keyword ideas.

**Parameters:**

- `keyword` (string): The seed keyword
- `country` (string): Country code (default: "us")
- `search_engine` (string): Search engine (default: "Google")

**Returns:**

```json
[
  {
    "keyword": "Example keyword",
    "volume": 1000,
    "difficulty": 45,
    "cpc": 2.5
  }
]
```

#### `get_traffic(domain_or_url: str, country: str = "None", mode: str = "subdomains")`

Get the traffic estimation.

**Parameters:**

- `domain_or_url` (string): The domain or URL to analyze
- `country` (string): Country filter (default: "None")
- `mode` (string): Analysis mode ("subdomains" or "exact")

**Returns:**

```json
{
  "traffic_history": [...],
  "traffic": {
    "trafficMonthlyAvg": 50000,
    "costMontlyAvg": 25000
  },
  "top_pages": [...],
  "top_countries": [...],
  "top_keywords": [...]
}
```

#### `keyword_difficulty(keyword: str, country: str = "us")`

Get the keyword difficulty score.

**Parameters:**

- `keyword` (string): The keyword to analyze
- `country` (string): Country code (default: "us")

**Returns:**

```json
{
  "difficulty": 45,
  "serp": [...],
  "related": [...]
}
```

## Development

For development:

```bash
git clone https://github.com/cnych/seo-mcp.git
cd seo-mcp
uv sync
```

## How it works

1. The user sends a request through MCP
2. The service uses CapSolver to solve the Cloudflare Turnstile CAPTCHA
3. The service gets the authentication token from Ahrefs
4. The service retrieves the requested SEO data
5. The service processes and returns the formatted results

## Troubleshooting

- **CapSolver API key error**：Check the `CAPSOLVER_API_KEY` environment variable
- **Rate limiting**：Reduce request frequency
- **No results**：The domain may not be indexed by Ahrefs
- **Other issues**：See [GitHub repository](https://github.com/cnych/seo-mcp)

## License

MIT License - See LICENSE file
