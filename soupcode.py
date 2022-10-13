from bs4 import BeautifulSoup

with open("candidates/Application from Phyllis Agu for Licensed Vocational Nurse.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')

name = ""
location = ""

# find name
for div in soup.h1:
    name = div
name = name.strip()
name += " LVN "

scr = ""
phone = ""
email = ""
date = ""

scr = soup.find(class_="side_content ats_content").p.string
scr = str(scr)
scr = scr[:scr.find(',')]
scr = '(' + scr + ')'
name += scr
name = name.strip()

###############
for text in soup.find_all(class_="textPhone"):
    phone = text
phone = phone.string

for mail in soup.find_all(class_="textEmail"):
    email = mail
email = mail.string

date = soup.find(class_="text applied_date").span.string

date2 = ""


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
    date2 += findMonth("Jun")
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

location = scr[1:len(scr)-1].strip()

info = [name, phone, email, date, location]
print(info)
info[0] = name[:name.find("LVN")-1]
info = [name, "Zip Recruiter", location, phone, email, date, "LVN - "]
print(info)
print(date)
print(name)
print(phone)
print(email)
print("location: " + location)
"""

fetch("https://search.dca.ca.gov/results", {
  "headers": {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
  },
  "referrer": "https://search.dca.ca.gov/",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": "boardCode=0&licenseType=248&licenseNumber=&firstName=rose&lastName=arenas&registryNumber=",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
}); ;

"""
