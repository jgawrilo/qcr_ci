import requests
import json

headers = {'Content-Type': 'application/json'}

data = json.load(open("./test_input2.json"))

url = "http://localhost:5001/api/impact"

response = requests.post(url,data=json.dumps({"data":data}),headers=headers)

print json.dumps(response.json(),indent=2)
