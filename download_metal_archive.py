import time

import requests
import json 
import pandas as pd

def parse_data(band_data):
    """ For each band, we will parse the data to return some dictionary
    """
    data = {
            'name': band_data[0].split("'>")[1].split("</")[0],
            'country': band_data[1],
            'genre': band_data[2],
            'status': band_data[3].split('>')[1].split('<')[0],
            'link': band_data[0].split("href='")[1].split("'>")[0]
        }
    return data

def download_url(letter, display_start):
    """
    We'll be using this function to download a couple of data for a certain alphabet letter.
    For example, if we insert 'a', this function will download data for bands that start with the letter A.
    Besides that, the page only can handle 500 bands at once, so we have to change display_start until we 
    aren't getting anything. We will test this by checking the length of the response.
    """
    print(letter, display_start)
    letter = letter.upper()
    display_start = display_start * 500
    epoch_time = get_current_epoch_time()
    url = f"https://www.metal-archives.com/browse/ajax-letter/l/{letter}/json/1?sEcho=2&iColumns=4&sColumns=&iDisplayStart={display_start}&iDisplayLength=500&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=false&_={epoch_time}"
    print(url)

    text = requests.get(url, headers={'User-Agent': ''}).text # By default user-agent is python-requests, for which query parameters are ignored
    json_data = json.loads(text)
    data_json = json_data['aaData']
    if len(data_json) == 0:
        return None
    print(data_json[0][0])
    return list(map(parse_data, data_json))


def get_current_epoch_time():
    epoch_time = round(time.time() * 1000)
    return epoch_time


def download_letter(letter):
    """
    This function downloads data for a certain letter. It relies on download_url function.
    """
    letter_data = []
    for i in range(1000):
        try:
            prov_data = download_url(letter, i)
            if prov_data is None:
                pd.DataFrame(letter_data).to_csv(f"{letter}.csv", index=None)
                return None
            else:
                letter_data = letter_data + prov_data
        except Exception as e:
            print(e)

for letter in 'ABCDEFGHIJKLMNOPQRSTUVXWYZ~':
    print(f"Downloading for letter {letter}")
    download_letter(letter)

# Special case for '#'
download_letter('NBR')
