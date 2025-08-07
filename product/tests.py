from django.test import TestCase
# import threading
# import requests
# from requests.auth import HTTPBasicAuth

# def place_bid(bid_amount):
#     try:
#         response = requests.patch(
#             "http://localhost:8000/auctions/1/bid/",
#             json={"bid_amount": bid_amount},
#             auth=HTTPBasicAuth("Alaa_algharbi", "12345"),
#             headers={"Content-Type": "application/json"}
#         )
#         try:
#             data = response.json()
#         except ValueError:
#             data = response.text
#         print(f"BID {bid_amount} => Status: {response.status_code} | Response: {data}")
#     except Exception as e:
#         print(f"BID {bid_amount} => ERROR: {e}")
# # محاكاة تقديم عرضين في نفس الوقت
# t1 = threading.Thread(target=place_bid, args=(308,))
# t2 = threading.Thread(target=place_bid, args=(309,))
# t3 = threading.Thread(target=place_bid, args=(310,))
# t4 = threading.Thread(target=place_bid, args=(311,))

# t1.start()
# t2.start()
# t3.start()
# t4.start()
# t1.join()
# t2.join()
# t3.join()
# t4.join()
