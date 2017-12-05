# Disable IPV6 because this stops it from being able to reach security.ubuntu.com 
# during the apt-get update for some reason
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.lo.disable_ipv6 = 1" >> /etc/sysctl.conf
sysctl -p

# install docker
apt-get update
apt-get install docker.io -y

# setup data directory
mkdir data
mv dataset.tar.gz data/
cd data
tar -zxvf dataset.tar.gz # I put this file in /root myself using scp before running this script
rm dataset.tar.gz
cd ..

# create the docker-compose file
echo "version: '3'" >> docker-compose.yml
echo "" >> docker-compose.yml
echo "services:" >> docker-compose.yml
echo "  ui-server:" >> docker-compose.yml
echo "    image: pjtatlow/geney-ui:0.0.3" >> docker-compose.yml
echo "    ports:" >> docker-compose.yml
echo "      - "80:80"" >> docker-compose.yml
echo "  backend-server:" >> docker-compose.yml
echo "    image: pjtatlow/geney-server:0.0.3" >> docker-compose.yml
echo "    volumes:" >> docker-compose.yml
echo "      - "./data:/root/data"" >> docker-compose.yml
echo "    environment:" >> docker-compose.yml
echo "      - GUNICORN_CMD_ARGS=--workers=4 --bind=:8888 --worker-class=eventlet --worker-connections 100" >> docker-compose.yml
echo "      - GENEY_DATA_PATH=/root/data" >> docker-compose.yml

# install docker-compose
curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.17.1/docker-compose-$(uname -s)-$(uname -m)"
chmod +x /usr/local/bin/docker-compose

docker-compose up -d # run docker compose in detatched mode