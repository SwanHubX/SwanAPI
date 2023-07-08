import requests

url = "http://127.0.0.1:8000/predictions/"

files = [('image', ('test.jpg', open('./test.jpg', 'rb'), 'image/jpeg'))]

response = requests.request("POST", url, files=files)

print(response.text)