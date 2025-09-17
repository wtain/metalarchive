from MetalArchivesApi import MetalArchivesApi

api = MetalArchivesApi()

slayer_discography = list(api.get_discography(72))

album_items = list(api.get_album_items(slayer_discography[0]))

print(album_items)

lyrics = api.get_lyrics(album_items[0]['lyrics_id'])

print(lyrics)