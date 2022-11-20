event ="https://www.ziprecruiter.com/candidates?q=&label_name=&interest=&show_hidden=0&status=&great=0&invite=0&applied_date=&my_candidates=0&max_distance=&quiz_id=8eadf980&page=1&rows=50#/"
reg = 'https://www.ziprecruiter.com/candidates?quiz_id=8eadf980'
user = 'https://www.ziprecruiter.com/contact/response/8eadf980/4b09b0b6?q=&label_name=&interest=&show_hidden=0&status=&great=0&invite=0&applied_date=&my_candidates=0&max_distance=&quiz_id=8eadf980&page=1&rows=50&total=26&search_id=1fb2299a-ee65-4db2-becb-d0a17bf921f5&pos=1#tabOriginalResume'
text = event
link = event

if (link.find('quiz_id') > 182):
    link = 'https://www.ziprecruiter.com/candidates?' + link[link.find('quiz_id'):]
print(link)
category = link[link.find(' ')+1:]
link = link[:link.find(' ')+1]

    # re = requests.post(url='http://127.0.0.1:8000/openstring', headers={'accept': 'application/json', 'Content-Type': 'application/json'}, json={'link': link, 'category': category})