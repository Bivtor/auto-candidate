import requests

apiKey = "stop"
apiUrl = "https://api.monday.com/v2"
headers = {"Authorization" : apiKey, "API-version" : 2023-04}

query2 = 'query { boards (limit:1) {id name} }'
data = {'query' : query2}

r = requests.post(url=apiUrl, json=data, headers=headers)