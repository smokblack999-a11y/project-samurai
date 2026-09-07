from .database import connect

def add_inventory(items):
    ids=[]
    with connect() as conn:
        for item in items:
            cur=conn.execute("INSERT INTO inventory(name,quantity,unit_price_minor,currency) VALUES(?,?,?,?)",(item.name,item.quantity,item.unit_price_minor,item.currency))
            ids.append(cur.lastrowid)
        conn.commit()
    return ids

def list_inventory():
    with connect() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM inventory ORDER BY id DESC").fetchall()]
