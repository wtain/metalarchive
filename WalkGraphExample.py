import heapq

from MetalArchivesApi import MetalArchivesApi

api = MetalArchivesApi()

start_band = "Children of Bodom"
threshold = 100
visited = { start_band }
to_visit = [(0, start_band)]
while to_visit:
    print(f"To visit: {len(to_visit)}, visited: {len(visited)}, top_score: {-to_visit[0][0]}")
    score, band_name = heapq.heappop(to_visit)
    score = -score
    if score and score < threshold:
        print(f"Terminating because of threshold {score} < {threshold}")
        break
    band = api.get_band(band_name)
    similar_bands = api.find_similar(band['id'])
    for similar_band in similar_bands:
        similar_band_name = similar_band['band_name']
        if similar_band_name in visited:
            continue
        visited.add(similar_band_name)
        heapq.heappush(to_visit, (-similar_band['score'], similar_band_name))
    print(visited)