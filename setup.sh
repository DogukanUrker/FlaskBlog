# make docker
docker build ./nginx -t businesscorpnginx
sudo docker run --rm -p 8000:80 businesscorpnginx