from typing import List, Optional, Any, Dict

import requests


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, bool):
            return default
        if isinstance(value, (int,)):
            return int(value)
        if isinstance(value, float):
            return int(round(value))
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    except Exception:
        pass
    return default


def _map_difficulty_label_to_int(label: Optional[str]) -> int:
    if not isinstance(label, str):
        return 0
    mapping = {
        "VeryEasy": 10,
        "Easy": 25,
        "Medium": 50,
        "Hard": 75,
        "VeryHard": 90,
        "SuperHard": 95,
    }
    return mapping.get(label, 0)


def _map_volume_label_to_int(label: Optional[str]) -> int:
    if not isinstance(label, str):
        return 0
    mapping = {
        "LessThanTen": 5,
        "TenToOneHundred": 50,
        "MoreThanOneHundred": 120,
        "Hundreds": 300,
        "Thousands": 1500,
        "TensOfThousands": 15000,
        "HundredsOfThousands": 150000,
        "Millions": 1500000,
    }
    return mapping.get(label, 0)


def format_keyword_ideas(keyword_data: Optional[List[Any]]) -> List[str]:
    if not keyword_data or len(keyword_data) < 2:
        return ["\n❌ No valid keyword ideas retrieved"]
    
    data = keyword_data[1]

    result = []
    
    # 处理常规关键词推荐
    if "allIdeas" in data and "results" in data["allIdeas"]:
        all_ideas = data["allIdeas"]["results"]
        # total = data["allIdeas"].get("total", 0)
        for idea in all_ideas:
            difficulty_value = idea.get('difficulty')
            volume_value = idea.get('volume')
            if difficulty_value is None:
                difficulty_value = _map_difficulty_label_to_int(idea.get('difficultyLabel'))
            else:
                difficulty_value = _coerce_int(difficulty_value, 0)
            if volume_value is None:
                volume_value = _map_volume_label_to_int(idea.get('volumeLabel'))
            else:
                volume_value = _coerce_int(volume_value, 0)

            simplified_idea = {
                "keyword": idea.get('keyword', 'No keyword'),
                "country": idea.get('country', '-'),
                "difficulty": difficulty_value,
                "volume": volume_value,
                "updatedAt": idea.get('updatedAt', '-')
            }
            result.append({
                "label": "keyword ideas",
                "value": simplified_idea
            })
    
    # 处理问题类关键词推荐
    if "questionIdeas" in data and "results" in data["questionIdeas"]:
        question_ideas = data["questionIdeas"]["results"]
        # total = data["questionIdeas"].get("total", 0)
        for idea in question_ideas:
            difficulty_value = idea.get('difficulty')
            volume_value = idea.get('volume')
            if difficulty_value is None:
                difficulty_value = _map_difficulty_label_to_int(idea.get('difficultyLabel'))
            else:
                difficulty_value = _coerce_int(difficulty_value, 0)
            if volume_value is None:
                volume_value = _map_volume_label_to_int(idea.get('volumeLabel'))
            else:
                volume_value = _coerce_int(volume_value, 0)

            simplified_idea = {
                "keyword": idea.get('keyword', 'No keyword'),
                "country": idea.get('country', '-'),
                "difficulty": difficulty_value,
                "volume": volume_value,
                "updatedAt": idea.get('updatedAt', '-')
            }
            result.append({
                "label": "question ideas",
                "value": simplified_idea
            })
    
    if not result:
        return ["\n❌ No valid keyword ideas retrieved"]
    
    return result


def get_keyword_ideas(token: str, keyword: str, country: str = "us", search_engine: str = "Google") -> Optional[List[str]]:
    if not token:
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeKeywordIdeas"
    payload = {
        "withQuestionIdeas": True,
        "captcha": token,
        "searchEngine": search_engine,
        "country": country,
        "keyword": ["Some", keyword]
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
