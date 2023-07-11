from swanapi import SwanRequests

response = SwanRequests(
    url="http://127.0.0.1:8000/predictions/",
    inputs={'text': 123})

print(response)