# BEGIN SET HOSTNAME
sudo hostnamectl set-hostname businessserver
# END SET HOSTNAME



# BEGIN DOCKER INSTALL

# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update -y

sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# END DOCKER INSTALL



# BEGIN BUILD CONTAINERS
# Prepare
docker network create --driver bridge businessnet 

# Setup
make docker
docker run --name reverse-proxy --restart always --rm -p 80:80 -d -v ./nginx/reverse-proxy.conf:/etc/nginx/nginx.conf:ro --network businessnet nginx

# BEGIN BUILD CONTAINERS

sudo reboot now