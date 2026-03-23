from typing import List, Optional, Any, Dict
import json

import requests


def _format_idea(idea: dict, label: str) -> str:
    return json.dumps({
        "label": label,
        "keyword": idea.get('keyword', 'No keyword'),
        "country": idea.get('country', '-'),
        "difficulty": idea.get('difficultyLabel', 'Unknown'),
        "volume": idea.get('volumeLabel', 'Unknown'),
        "updatedAt": idea.get('updatedAt', '-')
    })


def format_keyword_ideas(keyword_data: Optional[List[Any]]) -> List[str]:
    if not keyword_data or len(keyword_data) < 2:
        return ["No valid keyword ideas retrieved"]

    data = keyword_data[1]
    result = []

    if "allIdeas" in data and "results" in data["allIdeas"]:
        for idea in data["allIdeas"]["results"]:
            result.append(_format_idea(idea, "keyword ideas"))

    if "questionIdeas" in data and "results" in data["questionIdeas"]:
        for idea in data["questionIdeas"]["results"]:
            result.append(_format_idea(idea, "question ideas"))

    if not result:
        return ["No valid keyword ideas retrieved"]

    return result


def get_keyword_ideas(token: str, keyword: str, country: str = "us", search_engine: str = "Google") -> Optional[List[str]]:
    if not token:
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeKeywordIdeas"
    payload = {
        "withQuestionIdeas": True,
        "captcha": token,
        "searchEngine": [search_engine],
        "country": country,
        "keyword": keyword
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return None
    
    data = response.json()

    return format_keyword_ideas(data)


def get_keyword_difficulty(token: str, keyword: str, country: str = "us") -> Optional[Dict[str, Any]]:
    """
    Get keyword difficulty information
    
    Args:
        token (str): Verification token
        keyword (str): Keyword to query
        country (str): Country/region code, default is "us"
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing keyword difficulty information, returns None if request fails
    """
    if not token:
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeSerpOverviewForKeywordDifficultyChecker"
    
    payload = {
        "captcha": token,
        "country": country,
        "keyword": keyword
    }
    
    headers = {
        "accept": "*/*",
        "content-type": "application/json; charset=utf-8",
        "referer": f"https://ahrefs.com/keyword-difficulty/?country={country}&input={keyword}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            return None
        
        data: Optional[List[Any]] = response.json()
        # 检查响应数据格式
        if not isinstance(data, list) or len(data) < 2 or data[0] != "Ok":
            return None
        
        # 提取有效数据
        kd_data = data[1]
        
        # 格式化返回结果
        result = {
            "difficulty": kd_data.get("difficulty", 0),  # Keyword difficulty
            "shortage": kd_data.get("shortage", 0),      # Keyword shortage
            "lastUpdate": kd_data.get("lastUpdate", ""), # Last update time
            "serp": {
                "results": []
            }
        }
        
        # 处理SERP结果
        if "serp" in kd_data and "results" in kd_data["serp"]:
            serp_results = []
            for item in kd_data["serp"]["results"]:
                # 只处理有机搜索结果
                if item.get("content") and item["content"][0] == "organic":
                    organic_data = item["content"][1]
                    if "link" in organic_data and organic_data["link"][0] == "Some":
                        link_data = organic_data["link"][1]
                        result_item = {
                            "title": link_data.get("title", ""),
                            "url": link_data.get("url", [None, {}])[1].get("url", ""),
                            "position": item.get("pos", 0)
                        }
                        
                        # 添加指标数据（如果有）
                        if "metrics" in link_data and link_data["metrics"]:
                            metrics = link_data["metrics"]
                            result_item.update({
                                "domainRating": metrics.get("domainRating", 0),
                                "urlRating": metrics.get("urlRating", 0),
                                "traffic": metrics.get("traffic", 0),
                                "keywords": metrics.get("keywords", 0),
                                "topKeyword": metrics.get("topKeyword", ""),
                                "topVolume": metrics.get("topVolume", 0)
                            })
                        
                        serp_results.append(result_item)
            
            result["serp"]["results"] = serp_results
        
        return result
    except Exception:
        return None
