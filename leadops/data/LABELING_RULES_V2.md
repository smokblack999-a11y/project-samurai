# Labeling rules v2

1. `buying`: explicit price, order, payment, booking, purchase or immediate commercial intent.
2. `information`: product/service questions without purchase intent.
3. `support`: existing-customer operational problem.
4. `spam`: irrelevant or unsolicited noise.
5. `other`: ambiguous cases that should be reviewed.

Never infer identity, budget, location or purchase intent from private attributes. Annotators must label only evidence present in the message.
