from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import json
import time

#suchanfrage
searchterm = 'ryzen'
filepath = 'C:\\Users\\User\\Desktop\\Workspace\\' + searchterm +'.json'

# URL und Header für Webrequest
reg_url = "https://www.ebay-kleinanzeigen.de/s-pc-zubehoer-software/" + searchterm + "/k0c225"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}


def timestamp():
    return '[' + time.asctime(time.localtime()) + '] '

def return_items_from_req():
    # Webrequest
    print(timestamp() + 'sending web_request for term: \'' + searchterm + '\'')
    req = Request(url=reg_url, headers=headers) 
    html = urlopen(req).read()
    
    # HTMLparsing
    data =  BeautifulSoup(html, "html.parser" ).encode('UTF-8')
    soup = BeautifulSoup(data, features="html.parser")

    # finden der artikelliste in html
    result = soup.find('ul', {'id':'srchrslt-adtable', 'class':'itemlist-separatedbefore ad-list lazyload'})

    item_list_html = ''

    #Error Handling if HTML parse empty
    try:
        item_list_html = result.find_all('li', class_="ad-listitem lazyload-item")

    except:
        print(timestamp() + 'web_request error was handled')
        item_list_html = ''
    
    return item_list_html



def send_bot_msg(msg):
    # bot token
    token = '1526689152:AAHbUSuYCS9wZ9lP4CkgOvw7NpZkHtVQIZk'
    # meine chat id
    chat_id = '778752009'

    #url
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + msg
    results = requests.get(url_req)
    return results


def update_item_list(item_list_html):
    #öffne json file zum lesen und schreiben
    data = open(filepath, 'r')

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
            message = item_dict['id'] + '   ' + item_dict['name'] + '   ' + item_dict['price']
            print(timestamp() + 'sending bot_msg: ' + message)
            send_bot_msg(message)

    #als json abspeichern
    with open(filepath, 'w') as outfile:
        json.dump(item_list, outfile)

##########################################################################################################

#lade item liste
print(timestamp() + 'init item_list')
#öffne json file zum lesen und schreiben
data = open(filepath, 'r')

#lade json file in als artikel liste
item_list = json.load(data)

while True:
    # speichere die vorherige itemliste
    item_list_prev = item_list
    item_list = return_items_from_req()
    
    #wenn sich itemliste ändert
    if (item_list_prev != item_list) & (item_list != ''):
        update_item_list(item_list)

    #rollback to prev list
    if item_list == '':
        item_list = item_list_prev

    #pause between iterations in seconds
    time.sleep(10)