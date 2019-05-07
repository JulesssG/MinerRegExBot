import re, os, subprocess, io
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen

cmd1 = r'''/bin/grep -E "([A-Z]\w+[[:space:]])?([A-Z]\w+[[:space:]])?[A-Z]\w+[[:space:]]+[A-Z]\w+[[:space:]]+est[[:space:]]+né(e)?[[:space:]](\w+[[:space:]]+)*(le[[:space:]][0-9]+[[:space:]]\w+[[:space:]][0-9]+|en[[:space:]]+[0-9]+)(([[:space:]]|,|\.)+(à|au|Au|À)[[:space:]]+\w+([[:space:]]|\.|,))?" -o /home/lulu/EPFL/BA6/SHS-BA6/data/express.json'''
cmd2 = r'''/bin/grep -E "([A-Z]\w+[[:space:]])?([A-Z]\w+[[:space:]])?[A-Z]\w+[[:space:]]+[A-Z]\w+[[:space:]]+est[[:space:]]+né(e)?[[:space:]](\w+[[:space:]]+)*(le[[:space:]][0-9]+[[:space:]]\w+[[:space:]][0-9]+|en[[:space:]]+[0-9]+)(([[:space:]]|,|\.)+(à|au|Au|À)[[:space:]]+\w+([[:space:]]|\.|,))?" -o /home/lulu/EPFL/BA6/SHS-BA6/data/gazette.json'''

temp1 = subprocess.check_output(cmd1, shell=True)
temp2 = subprocess.check_output(cmd2, shell=True)

matches1 = temp1.decode('utf-8')
matches2 = temp2.decode('utf-8')

lines1 = matches1.split('\n')
lines2 = matches2.split('\n')

lines = lines1 + lines2

month_s_to_int = {'janvier': 1,'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'septembre': 9, 'octobre': 10,'novembre': 11, 'décembre': 12, '_janviet' : 1}

births = []

for m in lines:
    #print(m)

    name = ""
    location = ""
    year = 0
    month = 0
    day = 0

    # Name
    i = 0

    words = m.split()

    #print(words)

    for word in words:
        if word == "Le" or word == "Dr" or word == "Mlle" or word == "Mme" or word == "Mgr":
            i += 1
        elif len(word) > 0:
            if word[0].isupper():
                name += word + " "
                i += 1
            else:
                break
        else:
            i += 1

    #print(i)

    for word in words[i:]:
        i += 1
        if word == "né" or word == "née":
            break

    j = i
    while j < len(words):
        word = words[j]

        if word == "le":
            try:
                year = int(re.findall('\d+', words[j + 3])[0])
                #print(year)
                month = month_s_to_int.get(words[j + 2], 0)
                day = int(words[j + 1])
                j += 3
            except:
                j += 1
                continue

        if word == "à":
            location = "".join(re.findall("[a-zA-Z]+", words[j + 1]))
            j += 1

        if word == "en":
            try:
                year = int(words[j + 1])
            except:
                location = words[j + 1]


        # Iteration
        j += 1


    #print(i)
    #print(words[i:])

    if year < 1800 or year == 0:
        continue

    if location == "":
        location = "-"

    date = str(year) + "."

    if month != 0:
        date += str(month) + "."
        date += str(day)

    births.append([name, date, location])


data_naissance = births

dates = ""

for naissance in data_naissance:
    name = naissance[0]
    date = naissance[1]
    location = naissance[2]

    dates += "*[[" + date + "]] / [[" + location + "]]. Naissance de [[" + name + "]].\n"

user='MinerRegExBot'
passw='*********'
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'
names=['MinerRegExBot_output']

# Login request
payload={'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
r1=requests.post(baseurl + 'api.php', data=payload)

#login confirm
login_token=r1.json()['query']['tokens']['logintoken']
payload={'action':'login','format':'json','utf8':'','lgname':user,'lgpassword':passw,'lgtoken':login_token}
r2=requests.post(baseurl + 'api.php', data=payload, cookies=r1.cookies)

#get edit token2
params3='?format=json&action=query&meta=tokens&continue='
r3=requests.get(baseurl + 'api.php' + params3, cookies=r2.cookies)
edit_token=r3.json()['query']['tokens']['csrftoken']

edit_cookie=r2.cookies.copy()
edit_cookie.update(r3.cookies)

# changer le contenu
# écraser le contenu précédent:
for name in names:
        payload={'action':'edit','assert':'user','format':'json','utf8':'','text':dates,'summary':summary,'title':name,'token':edit_token}
        r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
        print(r4.text)
