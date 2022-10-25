
from __future__ import print_function
from ctypes.wintypes import POINT
from genericpath import isfile
from difflib import SequenceMatcher


import os
import os.path
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

import requests
from pathlib import Path
from bs4 import BeautifulSoup


def getTherapistInfo(path) -> list:
    """
    Find Name and Location from HTML (Therapist Specific)
    """
    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    name = ""
    location = ""

    # find name
    name = soup.find('h4', class_='name').string.strip()
    name += " Therapist "

    scr = ""
    phone = ""
    email = ""
    date = ""

    scr = soup.find(class_="side_content ats_content").find(
        'p', class_="location")

    # fixing no location exception
    if scr == None:
        scr = soup.find('a', class_='manage_job_link').stripped_strings
        for s in scr:
            scr = s
        scr = scr[scr.find(" - ")+3:]
    else:
        scr = scr.string

    # if (scr.string == None): scr = soup.find
    scr = str(scr)
    scr = scr[:scr.find(',')]
    scr = '(' + scr + ')'
    name += scr
    name = name.strip()
    location = scr[1:len(scr)-1].strip()

    ###############
    for text in soup.find_all(class_="textPhone"):
        phone = text
    phone = phone.string

    for mail in soup.find_all(class_="textEmail"):
        email = mail
    email = mail.string

    date = soup.find(class_="text applied_date").span.string

    date = cleanupdate(date)

    # update name to remove LVN (Location)
    nameonly = name[:name.find("Therapist")]

    # inputName = "Name: " + info[0] + "\n"
    # inputPhone = "Phone: " + info[1] + "\n"
    # inputEmail = "Email: " + info[2] + "\n"
    # inputDate = "Date Applied: " + info[3] + "\n"
    # inputLocation = "Location: " + info[4] + "\n"
    return [name, phone, email, date, location, nameonly.strip()]


def getLVNInfo(path) -> list:
    """
    Find Name and Location from HTML (LVN Specific)
    """
    with open(path) as fp:
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

    scr = soup.find(class_="side_content ats_content").find(
        'p', class_="location")

    # fixing no location exception
    if scr == None:
        scr = soup.find('a', class_='manage_job_link').stripped_strings
        for s in scr:
            scr = s
        scr = scr[scr.find(" - ")+3:]
    else:
        scr = scr.string

    scr = str(scr)
    scr = scr[:scr.find(',')]
    scr = '(' + scr + ')'
    name += scr
    name = name.strip()
    location = scr[1:len(scr)-1].strip()

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

    # update name to remove LVN (Location)
    nameonly = name[:name.find("LVN")]

    # inputName = "Name: " + info[0] + "\n"
    # inputPhone = "Phone: " + info[1] + "\n"
    # inputEmail = "Email: " + info[2] + "\n"
    # inputDate = "Date Applied: " + info[3] + "\n"
    # inputLocation = "Location: " + info[4] + "\n"
    return [name, phone, email, date, location, nameonly.strip()]


def cleanupdate_license(date):
    date2 = ""

    def findMonth(month: str):

        return date[date.find(" ")+1:date.find(",")] + "/" + date[date.find("202")+2:date.find("202")+4]

    if date.find("Jan"):
        date2 += "1/"
        date2 += findMonth("Jan")
    elif date.find("Feb"):
        date2 += "2/"
        date2 += findMonth("Feb")
    elif date.find("Mar"):
        date2 += "3/"
        date2 += findMonth("Mar")
    elif date.find("Apr"):
        date2 += "4/"
        date2 += findMonth("Apr")
    elif date.find("May"):
        date2 += "5/"
        date2 += findMonth("May")
    elif date.find("Jun"):
        date2 += "6/"
        date2 += findMonth("Jun")
    elif date.find("Jul"):
        date2 += "7/"
        date2 += findMonth("Jul")
    elif date.find("Aug"):
        date2 += "8/"
        date2 += findMonth("Aug")
    elif date.find("Sep"):
        date2 += "9/"
        date2 += findMonth("Sep")
    elif date.find("Oct"):
        date2 += "10/"
        date2 += findMonth("Oct")
    elif date.find("Nov"):
        date2 += "11/"
        date2 += findMonth("Nov")
    elif date.find("Dec"):
        date2 += "12/"
        date2 += findMonth("Dec")
    date = date2
    return date


def cleanupdate_ZR(date):

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


def getLVNnumber(name, depth):
    first = name[:name.rfind(" ")].strip()
    last = name[name.rfind(" "):].strip()
    url = "https://search.dca.ca.gov/results"
    body = "boardCode=0&licenseType=0&licenseNumber=&firstName={}&lastName={}&registryNumber=".format(
        first, last)
    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "if-none-match": 'W/"1e953a-vRUoGgQzuHnWBm/YM/qTtDChpnM"',
        "sec-ch-ua":
            '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            'referrer': "https://search.dca.ca.gov/",
            'referrerPolicy': "strict-origin-when-cross-origin",
            'body': "boardCode=0&licenseType=0&licenseNumber=&firstName=dane&lastName=miller&registryNumber=",
            'method': "POST",
            'mode': "cors",
            'credentials': "include",
    }

    r = requests.post(url, data=body, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    count = 0
    licenseinfolist = list()
    for i in soup.find_all('ul', class_="actions"):

        # define items to be collected
        name_found = ""
        licensetype = ""
        licensenumber = ""
        licenseexpiration = ""
        licenselocation = ""
        if count >= depth:
            break

        # get the s = similarity value from the first li
        name_found = ""
        if i.li.h3:
            name_found = str(i.li.h3.string).lower().strip()
            name_given = (last + ", " + first).lower()
            s = similar(name_found, name_given)
        else:
            continue

        # grab the info from the list items within each profile's ul element
        for j in i.find_all('li'):
            if str(j).find("License Number:") > 0:
                licensenumber = j.a.span.string
            if str(j).find("License Type:") > 0:
                licensetype = j.text[j.text.find(":")+2:]
            if str(j).find("Expiration Date:") > 0:
                licenseexpiration = j.text[j.text.find(":")+2:]
            if str(j).find("City:") > 0:
                licenselocation = str(j.span.text).lower()

         # append license info to return list
        licenseexpiration = cleanupdate_license(licenseexpiration)
        licenseinfolist.append(
            [name_found, licensetype, licensenumber, licenseexpiration, licenselocation, s])

        # if similarity of first string is very good then do not parse the next ones
        if s > .9:
            count += 1
            break
        # increment profiles parsed
        count += 1

    print("Got {} licenses for {}".format(count, name))

    return licenseinfolist


# x = getTherapistInfo("candidates/c8/Application from Billy Lee Wilson Jr. for Primary Therapist - AMFT, ACSW.html")
# print(x)
s = getLVNnumber('Victor Rinaldi', 5)
