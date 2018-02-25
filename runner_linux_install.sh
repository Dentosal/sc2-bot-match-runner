sudo apt-get update
sudo apt-get install -y python3-pip libltdl7 unzip
python3 --version
curl -O https://download.docker.com/linux/ubuntu/dists/artful/pool/stable/amd64/docker-ce_17.12.0~ce-0~ubuntu_amd64.deb
sudo dpkg -i docker-ce_17.12.0~ce-0~ubuntu_amd64.deb
cd /home/ubuntu/
git clone https://github.com/Dentosal/sc2-bot-match-runner.git
cd sc2-bot-match-runner
sudo usermod -a -G docker ubuntu
