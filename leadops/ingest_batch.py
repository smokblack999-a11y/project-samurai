from __future__ import annotations
import json
from data.anonymize import redact

def normalize(row:dict)->dict:
    return {"id":str(row["id"]),"text":redact(str(row["text"]))}

def convert(src:str,dst:str):
    count=0
    with open(src,encoding="utf-8") as f, open(dst,"w",encoding="utf-8") as out:
        for line in f:
            if not line.strip(): continue
            out.write(json.dumps(normalize(json.loads(line)),ensure_ascii=False)+"\n")
            count+=1
    return count
