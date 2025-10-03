from daily_digest import daily_digest
from storage_client.subscribers import subscribers_count_over_time

subscribers = subscribers_count_over_time()

print(subscribers)

daily_digest()
