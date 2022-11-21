import re
event = "https://www.ziprecruiter.com/candidates?q=&label_name=&interest=&show_hidden=0&status=&great=0&invite=0&applied_date=&my_candidates=0&max_distance=&quiz_id=8eadf980&page=1&rows=50#/"
reg = 'https://www.ziprecruiter.com/candidates?quiz_id=8eadf980'
user = 'https://www.ziprecruiter.com/contact/response/8eadf980/4b09b0b6?q=&label_name=&interest=&show_hidden=0&status=&great=0&invite=0&applied_date=&my_candidates=0&max_distance=&quiz_id=8eadf980&page=1&rows=50&total=26&search_id=1fb2299a-ee65-4db2-becb-d0a17bf921f5&pos=1#tabOriginalResume'
text = '<dsdsdssds>     add   https://www.ziprecruiter.com/candidates?quiz_id=8eadf980    Therapist '
text = '<dadsadsas>     text   Therapist 2    400'
# text = '   <dadsadsas>  text  Therapist  '
# text = event['text']
# @app.event("app_mention")


def event_test(event, say):
    text = event
    inputlist = re.sub(' +', ' ', text[text.find('>')+2:].strip()).split(' ')
    if len(inputlist) < 0:
        return
    method = inputlist[0]
    match method:
        case 'add':
            link = inputlist[1]
            category = inputlist[2]
            # print(requests.post(url='http://127.0.0.1:8000/openstring', headers={'accept': 'application/json', 'Content-Type': 'application/json'}, json={'link': link, 'category': category}))
            # say("Inputting Candidates in the {} Category".format(category))
        case 'text':
            category = inputlist[1]
            start = 2
            end = 998
            # if includes
            if len(inputlist) > 2:
                start = inputlist[2]
            if len(inputlist) > 3:
                end = inputlist[3]
            print(start)
            print(end)


event_test(text, "")
