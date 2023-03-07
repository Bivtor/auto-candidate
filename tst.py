from datetime import datetime
import re
event = "https://www.ziprecruiter.com/candidates?q=&label_name=&interest=&show_hidden=0&status=&great=0&invite=0&applied_date=&my_candidates=0&max_distance=&quiz_id=8eadf980&page=1&rows=50#/"
reg = 'https://www.ziprecruiter.com/candidates?quiz_id=8eadf980'
user = 'https://www.ziprecruiter.com/contact/response/8eadf980/4b09b0b6?q=&label_name=&interest=&show_hidden=0&status=&great=0&invite=0&applied_date=&my_candidates=0&max_distance=&quiz_id=8eadf980&page=1&rows=50&total=26&search_id=1fb2299a-ee65-4db2-becb-d0a17bf921f5&pos=1#tabOriginalResume'
text = '<dsdsdssds>     add   https://www.ziprecruiter.com/candidates?quiz_id=8eadf980    Therapist '
# text = '<dadsadsas>     text   Therapist 2    400'
# text = '   <dadsadsas>  text  Therapist  '
# text = event['text']
# @app.event("app_mention")

# TODO Known bugs: incorrect title
# TODO double check text contents, I think it uses the input from the text category


def event_test(event, say):
    text = event
    inputlist = re.sub(' +', ' ', text[text.find('>')+2:].strip()).split(' ')
    if len(inputlist) < 0:
        return
    method = inputlist[0]
    print(inputlist)
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

# TODO This could be improved massively but it should work for now


def cleanupdate(date: str, source: str):
    # If the source is ZipRecruiter
    if source == "ZipRecruiter":
        date2: str = ""

        def findMonth(month: str):
            return date[date.find(month)+4:date.find(",")] + "/" + date[date.find("202")+2:date.find("202")+4]
        if date.find("Jan") > 0:
            date2 += "1/"
            date2 += findMonth("Jan")
        elif date.find("Feb") > 0:
            date2 += "2/"
            date2 += findMonth("Feb")
        elif date.find("Mar") > 0:
            date2 += "3/"
            date2 += findMonth("Mar")
        elif date.find("Apr") > 0:
            date2 += "4/"
            date2 += findMonth("Apr")
        elif date.find("May") > 0:
            date2 += "5/"
            date2 += findMonth("May")
        elif date.find("Jun") > 0:
            date2 += "6/"
            date2 += findMonth("Jun")
        elif date.find("Jul") > 0:
            date2 += "7/"
            date2 += findMonth("Jul")
        elif date.find("Aug") > 0:
            date2 += "8/"
            date2 += findMonth("Aug")
        elif date.find("Sep") > 0:
            date2 += "9/"
            date2 += findMonth("Sep")
        elif date.find("Oct") > 0:
            date2 += "10/"
            date2 += findMonth("Oct")
        elif date.find("Nov") > 0:
            date2 += "11/"
            date2 += findMonth("Nov")
        elif date.find("Dec") > 0:
            date2 += "12/"
            date2 += findMonth("Dec")
        date = date2
        return date

    # If the source is indeed do this
    elif source == "Indeed":
        date_obj = datetime.strptime(date, '%b %d, %Y')
        return date_obj.strftime('%m/%d/%Y')


dates = ["Sep 26, 2022", "Sep 25, 2022"]
for date in dates:
    print(cleanupdate(date, "Indeed"))
# event_test(text, "")
