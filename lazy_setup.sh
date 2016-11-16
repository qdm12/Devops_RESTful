apt-get update -y
apt-get install git -y
git clone https://github.com/qdm12/Devops_RESTful.git

apt-get install virtualbox -y

curl https://releases.hashicorp.com/vagrant/1.8.7/vagrant_1.8.7_x86_64.deb > vagrant.deb
dpkg -i vagrant.deb
apt-get install -y
rm vagrant.deb

cd Devops_RESTful
vagrant up

sensible-browser localhost:5000
vagrant ssh -c "python /vagrant/server.py"


