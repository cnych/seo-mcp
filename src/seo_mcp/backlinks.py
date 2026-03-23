from typing import Any, List, Optional, Dict, Tuple, cast
import os
import json
import time
from datetime import datetime
import requests

# Cache file path for storing signatures
SIGNATURE_CACHE_FILE = "signature_cache.json"


def iso_to_timestamp(iso_date_string: str) -> float:
    """
    Convert ISO 8601 format datetime string to timestamp
    Example: "2025-04-12T14:59:18Z" -> 1744916358.0
    """
    # Handle UTC time represented by "Z"
    if iso_date_string.endswith('Z'):
        iso_date_string = iso_date_string[:-1] + '+00:00'
    dt = datetime.fromisoformat(iso_date_string)
    return dt.timestamp()



def save_signature_to_cache(signature: str, valid_until: str, overview_data: Dict[str, Any], domain: str) -> bool:
    """
    Save signature information to local cache file
    
    Args:
        signature: Obtained signature
        valid_until: Signature expiration time
        domain: Domain name
        
    Returns:
        True if saved successfully, False otherwise
    """
    # Read existing cache
    cache_data: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(SIGNATURE_CACHE_FILE):
        try:
            with open(SIGNATURE_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
        except:
            pass
    
    # Update cache for current domain
    cache_data[domain] = {
        "signature": signature,
        "valid_until": valid_until,
        "overview_data": overview_data,
        "timestamp": datetime.now().timestamp()
    }
    
    try:
        with open(SIGNATURE_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
        return True
    except Exception as e:
        return False


def load_signature_from_cache(domain: str) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    """
    Load signature information for a specific domain from local cache file
    Returns the signature and valid_until if cache is valid, otherwise None
    
    Args:
        domain: Domain to query
        
    Returns:
        (signature, valid_until) tuple, or (None, None) if no valid cache
    """
    if not os.path.exists(SIGNATURE_CACHE_FILE):
        return None, None, None
    
    try:
        with open(SIGNATURE_CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
        
        # Check if cache exists for current domain
        if domain not in cache_data:
            return None, None, None
        
        domain_cache = cache_data[domain]
        
        # Check if signature is expired
        valid_until = domain_cache.get("valid_until")
        
        if valid_until:
            # Convert ISO date string to timestamp for comparison
            valid_until_timestamp = iso_to_timestamp(valid_until)
            current_time = time.time()
            
            if current_time < valid_until_timestamp:
                return domain_cache.get("signature"), valid_until, domain_cache.get("overview_data")
            else:
                return None, None, None
        else:
            return None, None, None
    except Exception:
        return None, None, None



def get_signature_and_overview(token: str, domain: str) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    """
    Get signature and validUntil parameters using the token
    
    Args:
        token: Verification token
        domain: Domain to query
        
    Returns:
        (signature, valid_until, overview_data) tuple, or (None, None, None) if failed
    """
    url = "https://ahrefs.com/v4/stGetFreeBacklinksOverview"
    payload = {
        "captcha": token,
        "mode": "subdomains",
        "url": domain
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return None, None, None
    
    data = response.json()
    
    try:
        # Assuming data format is always ['Ok', {signature object}]
        if isinstance(data, list) and len(cast(List[Any], data)) > 1:
            second_element: Dict[str, Any] = cast(Dict[str, Any], data[1])
            signature: str = cast(str, second_element['signedInput']['signature'])
            valid_until: str = cast(str, second_element['signedInput']['input']['validUntil'])
            overview_data: Dict[str, Any] = cast(Dict[str, Any], second_element['data'])
            
            # Save the new signature to cache
            save_signature_to_cache(signature, valid_until, overview_data, domain)
            
            return signature, valid_until, overview_data
        else:
            return None, None, None
    except Exception:
        return None, None, None
    

def format_backlinks(backlinks_data: List[Any], domain: str) -> List[Any]:
    """
    Format backlinks data
    """
    if backlinks_data and len(backlinks_data) > 1 and "topBacklinks" in backlinks_data[1]:
        backlinks = backlinks_data[1]["topBacklinks"]["backlinks"]
        # Only keep necessary fields
        simplified_backlinks = []
        for backlink in backlinks:
            simplified_backlink = {
                "anchor": backlink.get("anchor", ""),
                "domainRating": backlink.get("domainRating", 0),
                "title": backlink.get("title", ""),
                "urlFrom": backlink.get("urlFrom", ""),
                "urlTo": backlink.get("urlTo", ""),
                "edu": backlink.get("edu", False),
                "gov": backlink.get("gov", False),
            }
            simplified_backlinks.append(simplified_backlink)
        return simplified_backlinks
    else:
        return []
    

def get_backlinks(signature: str, valid_until: str, domain: str) -> Optional[List[Any]]:
    if not signature or not valid_until:
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeBacklinksList"
    payload = {
        "reportType": ["TopBacklinks"],
        "signedInput": {
            "signature": signature,
            "input": {
                "validUntil": valid_until,
                "mode": "subdomains",
                "url": f"{domain}/"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return None
    
    data = response.json()

    return format_backlinks(data, domain)



def get_backlinks_overview(signature: str, valid_until: str, domain: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve backlinks overview data for a domain using Ahrefs API.
    
    Args:
        signature: The authentication signature
        valid_until: Signature expiration timestamp
        domain: The domain to get overview data for
        
    Returns:
        Dictionary containing backlinks overview data or None if request fails
    """
    if not signature or not valid_until:
        print("ERROR: No signature or valid_until, cannot proceed")
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeBacklinksOverview"
    payload = {
        "captcha": signature,
        "mode": "subdomains",
        "url": domain
    }
    
    headers = {
        "Content-Type": "application/json",
        "accept": "*/*",
        "sec-fetch-site": "same-origin"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"ERROR: Failed to get backlinks overview, status code: {response.status_code}, response: {response.text}")
            return None
        
        data = response.json()
        return data
    except Exception:
        return None
