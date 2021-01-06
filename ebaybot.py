from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os.path
import requests
import json
import time


#header für req
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

#erstelle timestamp im format: [Wed Jan  6 15:44:14 2021]
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

    #setze leere itemliste
    item_list_html = ''

    #Error Handling if HTML parse empty
    try:
        item_list_html = result.find_all('li', class_="ad-listitem lazyload-item")

    #wenn ein error auftritt handle diesen
    except Exception as e:
        print(timestamp() + 'Error Exception: ' + str(e))
        item_list_html = ''

    #gebe die itemliste zurück
    return item_list_html


def send_bot_msg(msg):
    # bot token
    token = '1526689152:AAHbUSuYCS9wZ9lP4CkgOvw7NpZkHtVQIZk'
    # meine chat id
    chat_id = '778752009'

    #url zusammenbauen
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + msg

    #req senden und resultate speichern
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

        #wenn suchen im string, dann überspringe artikel
        if not any("suche" in s for s in item_name.lower().split()): 

            #teile pricestr in wörter array
            item_price = item_price.split()
            
            #wenn erstes "wort" eine nummer ist dann nehme es als wert, sonst 0
            if item_price[0].isdigit():
                item_price = int(item_price[0])
            else:
                item_price = 0

            #wenn preis im zielpreis dann nimm artikel, sonst skip
            if (item_price >= minprice) & (item_price <= maxprice):

                #erstelle dictionary
                item_dict = {'id': item_id, 'name': item_name, 'price': item_price}

                #hänge aktuelles dictionary an liste an
                if item_dict not in item_list:
                    item_list.append(item_dict)
                    message = item_dict['name'] + '\n' + str(item_dict['price']) + '€'

                    item_link = "https://www.ebay-kleinanzeigen.de/s-anzeige/" + item_dict['id']

                    print(timestamp() + 'sending bot_msg: ' + item_dict['name'] + ' | ' + str(item_dict['price']) + '€')

                    send_bot_msg(message + '\n' + item_link)

    #als json abspeichern
    with open(filepath, 'w') as outfile:
        json.dump(item_list, outfile)

##########################################################################################################

#searchterm input und ' ' durch '-' ersetzen
searchterm = input(timestamp() + 'enter your searchterm: ').replace(' ', '-')

#sleeptime input
sleeptime = int(input(timestamp() + 'enter time(sec) to elapse between web-requests: '))

#minprice input
minprice = int(input(timestamp() + 'enter your lowest price: '))

#maxprice input
maxprice = int(input(timestamp() + 'enter your highest price: '))


#filepath für dazugehörige json erstellen
filepath = os.path.dirname(__file__) + '\\data\\' + searchterm +'.json'

# URL und Header für Webrequest
reg_url = "https://www.ebay-kleinanzeigen.de/s-pc-zubehoer-software/" + searchterm + "/k0c225"

#lade item liste
print(timestamp() + 'init item_list')

#wenn json file nicht existiert, dann erstelle diese
if not os.path.isfile(filepath):
    with open(filepath, "w") as text_file:
        text_file.write("[]")

#öffne json file zum lesen und schreiben
data = open(filepath, 'r')

#lade json file in als artikel liste
item_list = json.load(data)

#BotMessage
start_message = 'Starte Suche für \'' + searchterm + '\' zwischen ' + str(minprice) + '€ - ' + str(maxprice) + '€'
send_bot_msg(start_message)
print(timestamp() + 'sending bot_msg: ' + start_message)

while True:
    try:
        # speichere die vorherige itemliste
        item_list_prev = item_list
        item_list = return_items_from_req()
        
        #wenn sich itemliste ändert
        if (item_list_prev != item_list) & (item_list != ''):
            update_item_list(item_list)

        #rollback to prev list
        if item_list == '':
            item_list = item_list_prev

    except Exception as e:
        print(timestamp() + 'Error Exception: ' + str(e))

    #pause between iterations in seconds
    time.sleep(sleeptime)