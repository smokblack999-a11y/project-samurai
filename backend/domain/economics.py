def margin_percent(cost_minor:int,sale_minor:int)->float:
    if sale_minor<=0:return 0.0
    return round((sale_minor-cost_minor)/sale_minor*100,2)

def profit_minor(cost_minor:int,sale_minor:int,quantity:float)->int:
    return round((sale_minor-cost_minor)*quantity)
