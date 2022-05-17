import iapp_ai
api = iapp_ai.api("iapp-website")
print(api.idcard_front("media/id-card-front.jpg"))
print("----")
print(api.idcard_front("media/id-card-front.jpg", additional_headers={"apikey":"123"}))