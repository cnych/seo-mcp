import os
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent.parent / "src"))

from seo_mcp.backlinks import (
    get_backlinks,
    get_signature_and_overview,
    load_signature_from_cache,
)
from seo_mcp.keywords import get_keyword_ideas, get_keyword_difficulty
from seo_mcp.traffic import check_traffic
from seo_mcp.server import get_capsolver_token

app = FastAPI(
    title="SEO MCP API",
    description="HTTP API wrapper for SEO MCP tools - keyword research, backlinks, and traffic analysis",
    version="1.0.0"
)

api_key = os.environ.get("CAPSOLVER_API_KEY")

class KeywordRequest(BaseModel):
    keyword: str
    country: str = "us"
    search_engine: str = "Google"

class BacklinksRequest(BaseModel):
    domain: str

class TrafficRequest(BaseModel):
    domain_or_url: str
    country: str = "None"
    mode: Literal["subdomains", "exact"] = "subdomains"

class KeywordDifficultyRequest(BaseModel):
    keyword: str
    country: str = "us"

@app.get("/")
async def root():
    return {
        "message": "SEO MCP API",
        "endpoints": {
            "keyword_ideas": "/keyword-ideas",
            "keyword_difficulty": "/keyword-difficulty", 
            "backlinks": "/backlinks",
            "traffic": "/traffic"
        }
    }

def get_capsolver_token_fixed(site_url: str, *, max_create_attempts: int = 3, max_wait_seconds: int = 60) -> Optional[str]:
    """CapSolver token with retries and timeout, matching server logic for errorId handling."""
    import requests

    api_key = os.environ.get("CAPSOLVER_API_KEY")

    if not api_key:
        return None

    for attempt in range(1, max_create_attempts + 1):
        payload = {
            "clientKey": api_key,
            "task": {
                "type": 'AntiTurnstileTaskProxyLess',
                "websiteKey": "0x4AAAAAAAAzi9ITzSN9xKMi",
                "websiteURL": site_url,
                "metadata": {"action": ""}
            }
        }
        try:
            res = requests.post("https://api.capsolver.com/createTask", json=payload, timeout=30)
            resp = res.json()
        except Exception as e:
            continue

        task_id = resp.get("taskId")
        if not task_id:
            continue

        start = time.time()
        while True:
            if time.time() - start > max_wait_seconds:
                break
            time.sleep(1)
            try:
                result_payload = {"clientKey": api_key, "taskId": task_id}
                result_res = requests.post("https://api.capsolver.com/getTaskResult", json=result_payload, timeout=30)
                result_data = result_res.json()
            except Exception as e:
                continue

            status = result_data.get("status")
            if status == "ready":
                token = result_data.get("solution", {}).get("token")
                return token
            if status == "failed" or result_data.get("errorId"):
                break
            # else processing
        # try creating a new task on next attempt

    return None

@app.get("/health")
async def health():
    return {
        "ok": True,
        "api_key_present": bool(os.environ.get("CAPSOLVER_API_KEY")),
        "cwd": str(Path.cwd()),
        "endpoints": ["/keyword-ideas", "/keyword-difficulty", "/backlinks", "/traffic"],
    }

@app.post("/keyword-ideas")
async def keyword_ideas(request: KeywordRequest):
    try:
        encoded_keyword = urllib.parse.quote(request.keyword)
        site_url = f"https://ahrefs.com/keyword-generator/?country={request.country}&input={encoded_keyword}"
        token = get_capsolver_token_fixed(site_url)
        
        if not token:
            raise HTTPException(status_code=500, detail="Failed to get verification token")
        
        result = get_keyword_ideas(token, request.keyword, request.country, request.search_engine)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to get keyword ideas")
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/keyword-difficulty")
async def keyword_difficulty(request: KeywordDifficultyRequest):
    try:
        encoded_keyword = urllib.parse.quote(request.keyword)
        site_url = f"https://ahrefs.com/keyword-difficulty/?country={request.country}&input={encoded_keyword}"
        token = get_capsolver_token_fixed(site_url)
        
        if not token:
            raise HTTPException(status_code=500, detail="Failed to get verification token")
        
        result = get_keyword_difficulty(token, request.keyword, request.country)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to get keyword difficulty")
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backlinks")
async def backlinks(request: BacklinksRequest):
    try:
        # 1) Try cache (signature + validUntil + overview)
        signature, valid_until, overview = load_signature_from_cache(request.domain)

        # 2) If cache miss/expired: solve captcha and fetch signature
        if not signature or not valid_until:
            site_url = f"https://ahrefs.com/backlink-checker/?input={request.domain}&mode=subdomains"
            token = get_capsolver_token_fixed(site_url)
            if not token:
                raise HTTPException(status_code=500, detail="Failed to get verification token")
            sig, vu, ov = get_signature_and_overview(token, request.domain)
            if not sig or not vu:
                raise HTTPException(status_code=500, detail="Failed to get signature")
            signature, valid_until, overview = sig, vu, ov

        # 3) Fetch backlinks with signature
        backlinks_list = get_backlinks(signature, valid_until, request.domain)
        if backlinks_list is None:
            raise HTTPException(status_code=500, detail="Failed to get backlinks")

        return {"success": True, "data": {"overview": overview, "backlinks": backlinks_list}}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/traffic")
async def traffic(request: TrafficRequest):
    try:
        site_url = f"https://ahrefs.com/traffic-checker/?input={request.domain_or_url}&mode={request.mode}"
        token = get_capsolver_token_fixed(site_url)
        
        if not token:
            raise HTTPException(status_code=500, detail="Failed to get verification token")
        
        result = check_traffic(token, request.domain_or_url, request.mode, request.country)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to get traffic data")
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)