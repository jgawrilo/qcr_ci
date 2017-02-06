import requests
import json

headers = {'Content-Type': 'application/json'}

data = json.load(open("./test_input.json"))

url = "http://localhost:5001/api/impact"

response = requests.post(url,data=json.dumps({"data":data}),headers=headers)

print response.json()