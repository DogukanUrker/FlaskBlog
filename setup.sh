# Prepare
docker network create --driver bridge businessnet 

# Setup
make docker
docker run --name reverse-proxy --rm -p 8000:80 -d -v ./nginx/reverse-proxy.conf:/etc/nginx/nginx.conf:ro --network businessnet nginx

echo "Press enter to stop"
read na
echo "Tearing down"

# Teardown
docker stop flaskblog
docker stop reverse-proxy
docker network rm businessnet