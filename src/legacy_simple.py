import os
import re
import json
import time
import argparse
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-e8fa331ebdae4229b52967d9528649ed")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

TIMEOUT = 60
RETRY = 2


def _headers() -> Dict[str, str]:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY")
    return {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }


def _post(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    last_err = None
    for i in range(RETRY + 1):
        try:
            r = requests.post(url, headers=_headers(), json=payload, timeout=TIMEOUT)
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(0.4 * (i + 1))
    raise RuntimeError(f"request failed: {last_err}")


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": MODEL,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    data = _post(url, payload)
    return data["choices"][0]["message"]["content"]


def sloppy_json(text: str) -> Dict[str, Any]:
    """
    期望输出 JSON，但这里解析很脆弱：
    - 先找 ```json ... ```
    - 再找第一个 {...}
    - 失败就兜底返回
    """
    text = (text or "").strip()

    m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass

    m2 = re.search(r"(\{.*\})", text, flags=re.S)
    if m2:
        candidate = m2.group(1).strip().replace("'", '"')
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return {"result": text[:1000], "format_error": True}


def run_task(task: str, mode: str = "rewrite", temperature: float = 0.2) -> Dict[str, Any]:
    """
    mode:
      - rewrite: 改写句子，更礼貌
      - extract: 从文本里提取信息，输出 JSON
    这里把 prompt 写得很乱，且两个模式混在一起。
    """
    system = "你是一个中文助手。请务必遵守用户的输出格式要求。"
    if mode == "rewrite":
        # 乱：把规则写在 user 里
        user = f"""
请把下面内容改写得更礼貌、更职业，保留原意。
只输出改写后的文本，不要解释。

内容：
{task}
"""
        raw = call_llm(system, user, temperature=temperature)
        return {"mode": mode, "output": raw.strip(), "raw": raw[:1200]}

    # extract 模式：要求 JSON，但没有结构化约束
    user = f"""
从下面文本中提取信息，必须输出 JSON，字段：
- summary: string
- action_items: string[]
- tone: string (例如: 正面/中性/负面)

只输出 JSON，不要输出任何多余文字。

文本：
{task}
"""
    raw = call_llm(system, user, temperature=temperature)
    parsed = sloppy_json(raw)
    parsed["mode"] = mode
    parsed["raw"] = raw[:1200]
    return parsed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=str, required=True)
    p.add_argument("--mode", type=str, default="rewrite", choices=["rewrite", "extract"])
    p.add_argument("--temperature", type=float, default=0.2)
    args = p.parse_args()

    res = run_task(args.task, mode=args.mode, temperature=args.temperature)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()