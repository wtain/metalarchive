import requests
import json
import bs4


# https://metal-api.dev/index.html
class MetalArchivesApi:

    def __init__(self):
        pass

    def search_by_name(self, band_name):
        result = requests.get(f"https://metal-api.dev/search/bands/name/{band_name}")
        if result.status_code != 200:
            print(f"Warning: {result.status_code}")
            return []
        return json.loads(result.content)

    def get_band(self, name):
        bands = self.search_by_name(name)
        if len(bands) == 0:
            return None
        return bands[0]

    def _get_document(self, url):
        html = requests.get(url).text
        return bs4.BeautifulSoup(html, 'html.parser')

    def get_discography(self, band_id):
        content = self._get_document(
            f"https://www.metal-archives.com/band/discography/id/{band_id}/tab/all")
        table = content.find('table')
        if not table:
            return
        tbody = table.find("tbody")
        for child in tbody.findChildren('tr'):
            tds = child.findChildren('td')
            link = tds[0].find('a')
            album_url = link['href']
            album_id = album_url.split('/')[-1]
            release_name = link.string
            release_type = tds[1].string
            release_year = int(tds[2].string)
            yield {
                "name": release_name,
                "type": release_type,
                "year": release_year,
                "album_id": album_id,
                "album_url": album_url
            }

    def get_album_items(self, album_data):
        content = self._get_document(album_data['album_url'])
        table = content.find('table', class_='table_lyrics')
        if not table:
            return
        tbody = table.find("tbody")
        for child in tbody.findChildren('tr'):
            if not set.intersection(set(child.attrs.get('class', [])), {'even', 'odd'}):
                continue
            tds = child.findChildren('td')
            name = tds[1].string.strip()
            lyrics_id = "".join(filter(str.isnumeric, tds[3].findChildren('a')[0]['href']))
            duration = tds[2].string
            yield {
                "name": name,
                "duration": duration,
                "lyrics_id": lyrics_id
            }

    def get_lyrics(self, lyrics_id):
        return ((requests.get(f"https://www.metal-archives.com/release/ajax-view-lyrics/id/{lyrics_id}")
                 .content
                 .decode('utf-8')
                .replace('<br />', ''))
                .replace('\t', ''))

    def find_similar(self, band_id):
        content = self._get_document(f"https://www.metal-archives.com/band/ajax-recommendations/id/{band_id}/showMoreSimilar/1")

        table = content.find('table', id="artist_list")
        if not table:
            return
        tbody = table.find("tbody")
        for child in tbody.findChildren('tr'):
            link = child.find('a')
            span = child.find('span')
            if not span:
                continue
            score = int(span.string)
            yield {
                "band_name": link.string,
                "score": score
            }
