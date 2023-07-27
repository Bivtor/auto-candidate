import requests

apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI2OTM4NzUxOSwiYWFpIjoxMSwidWlkIjo0NTgxNDc2NywiaWFkIjoiMjAyMy0wNy0xOFQwMjo0OTo1My4wNjZaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTc4NjM4NjAsInJnbiI6InVzZTEifQ.6aI2-fuA_ThOX5lXEShu_uGrPbmwYmf6isgI5GuzXO0"
apiUrl = "https://api.monday.com/v2"
headers = {"Authorization" : apiKey, "API-version" : 2023-04}

query2 = 'query { boards (limit:1) {id name} }'
data = {'query' : query2}

r = requests.post(url=apiUrl, json=data, headers=headers)