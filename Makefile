build:
	docker build -t channel-stats .

run: build
# .env file - only for local runs
# host network - is discouraged to use
# use docker-compose?
	docker run --network host --env-file .env channel-stats