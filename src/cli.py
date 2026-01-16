# src/cli.py
# -*- coding: utf-8 -*-

import json
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.refactor_chain import run_rewrite, run_extract

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True, type=str)
    p.add_argument(
        "--mode",
        default="rewrite",
        choices=["rewrite", "extract"],
    )
    args = p.parse_args()

    if args.mode == "rewrite":
        result = run_rewrite(args.task)
        print(json.dumps(
            {"mode": "rewrite", "output": result},
            ensure_ascii=False,
            indent=2,
        ))
    else:
        result = run_extract(args.task)
        print(json.dumps(
            {
                "mode": "extract",
                "summary": result.summary,
                "action_items": result.action_items,
                "tone": result.tone,
            },
            ensure_ascii=False,
            indent=2,
        ))


if __name__ == "__main__":
    main()
