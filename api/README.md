# SEO MCP HTTP API

Simple HTTP API wrapper for the SEO MCP tools.

## Quick Start

1. Install dependencies:
```bash
cd api
pip install -r requirements.txt
```

2. Set environment variable:
```bash
set CAPSOLVER_API_KEY=your-api-key-here
```

3. Run the server:
```bash
python main.py
```

4. Access the API at: http://localhost:8000

## API Endpoints

### GET /
Returns API information and available endpoints.

### POST /keyword-ideas
Get keyword suggestions for a given keyword.

**Request:**
```json
{
  "keyword": "website design",
  "country": "us",
  "search_engine": "Google"
}
```

### POST /keyword-difficulty
Get keyword difficulty score.

**Request:**
```json
{
  "keyword": "website design",
  "country": "us"
}
```

### POST /backlinks
Get backlink information for a domain.

**Request:**
```json
{
  "domain": "example.com"
}
```

### POST /traffic
Get traffic estimates for a domain.

**Request:**
```json
{
  "domain_or_url": "example.com",
  "country": "None",
  "mode": "subdomains"
}
```

## Testing with curl

```bash
# Test keyword ideas
curl -X POST "http://localhost:8000/keyword-ideas" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "website design", "country": "gb"}'

# Test traffic
curl -X POST "http://localhost:8000/traffic" \
  -H "Content-Type: application/json" \
  -d '{"domain_or_url": "google.com"}'
```

## n8n Integration

In n8n, use HTTP Request nodes with:
- Method: POST
- URL: http://your-server:8000/keyword-ideas
- Body: JSON with the required parameters

## Production Deployment

For production, consider:
- Using a proper WSGI server (gunicorn)
- Adding authentication/rate limiting
- Setting up monitoring
- Using environment variables for configuration