docker rmi -f $(docker images -a -q)
docker rm -vf $(docker ps -a -q)
docker system prune -a --volumes
