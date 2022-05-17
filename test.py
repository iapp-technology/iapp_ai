#Example

import iapp_ai
api = iapp_ai.api("iapp-website")
#Normal usage
print(api.idcard_front("media/id-card-front.jpg"))
print("----")
#Change apikey to the invalid one.
print(api.idcard_front("media/id-card-front.jpg", headers={"apikey":"123"}))