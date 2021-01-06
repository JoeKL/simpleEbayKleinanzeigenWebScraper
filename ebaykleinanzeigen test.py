from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import json

searchterm = 'ryzen-7-3700x'

def send_bot_msg(msg):
    # bot token
    token = '1526689152:AAHbUSuYCS9wZ9lP4CkgOvw7NpZkHtVQIZk'
    # meine chat id
    chat_id = '778752009'

    #url
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + msg
    results = requests.get(url_req)
    return results

# URL und Header für Webrequest
reg_url = "https://www.ebay-kleinanzeigen.de/s-pc-zubehoer-software/" + searchterm + "/k0c225"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

# Webrequest
req = Request(url=reg_url, headers=headers) 
html = urlopen(req).read()

# HTMLparsing
data =  BeautifulSoup(html, "html.parser" ).encode('UTF-8')
soup = BeautifulSoup(data, features="html.parser")

# finden der artikelliste in html
result = soup.find('ul', {'id':'srchrslt-adtable', 'class':'itemlist-separatedbefore ad-list lazyload'})
item_list_html = result.find_all('li', class_="ad-listitem lazyload-item")

#öffne json file zum lesen und schreiben
data = open(searchterm + '.json', 'r')

#lade json file in als artikel liste
item_list = json.load(data)


for item in item_list_html:  
    #finde id, name und price des artikels
    item_id = item.article['data-adid']
    item_name = item.find('div', class_="aditem-main").h2.a.text
    item_price = item.find('div', class_="aditem-details").strong.text

    #erstelle dictionary
    item_dict = {'id': item_id, 'name': item_name, 'price': item_price}

    #hänge aktuelles dictionary an liste an
    if item_dict not in item_list:
        item_list.append(item_dict)
        send_bot_msg(item_dict['id'] + '   ' + item_dict['name'] + '   ' + item_dict['price'])

#gebe liste aus
# print(item_list)

#als json abspeichern
with open(searchterm + '.json', 'w') as outfile:
    json.dump(item_list, outfile)