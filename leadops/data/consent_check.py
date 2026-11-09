from __future__ import annotations
import json
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: consent_check.py authorization.json')
    with open(sys.argv[1], encoding='utf-8') as f:
        data=json.load(f)
    if data.get('authorized') is not True:
        raise SystemExit('pilot dataset authorization is required')
    print('authorization=ok')
