# BEGIN SET HOSTNAME
sudo hostnamectl set-hostname businessserver
# END SET HOSTNAME



# BEGIN DOCKER INSTALL

# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update



sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# END DOCKER INSTALL



# BEGIN REGISTER START WEBSERVER ON LOAD

# Source - https://stackoverflow.com/a/878647
# Posted by dogbane, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-09, License - CC BY-SA 3.0

#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "@reboot ./start-bsides-proxyserver.sh" >> mycron
#install new cron file
crontab mycron
rm mycron

# END REGISTER START WEBSERVER ON LOAD


sudo reboot now