import hashlib,json
def key_for(payload:dict)->str: return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
