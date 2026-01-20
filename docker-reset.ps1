docker compose down -v --rmi all --remove-orphans
docker system prune -a -f --volumes
docker network prune -f
docker builder prune -f
docker volume prune -f