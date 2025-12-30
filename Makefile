build:
	docker build -t channel-stats .

run: build
# .env file - only for local runs
# host network - is discouraged to use
# use docker-compose?
	# docker run --network host -p 127.0.0.1:8001:8001 --env-file .env channel-stats
	# docker run --network appnet -p 8001:8001 --env-file .env channel-stats
	docker run --network storage_appnet -p 8001:8001 --env-file .env channel-stats