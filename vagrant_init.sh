#!/usr/bin/env bash

#sudo sh -c 'echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list'
#sudo sh -c 'echo "deb http://cran.stat.auckland.ac.nz/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list'
#gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
#gpg -a --export E084DAB9 | sudo apt-key add -

apt-get -y update
apt-get -y upgrade

apt-get -y install python-pip python-setuptools python-dev build-essential libssl-dev libffi-dev



#sudo apt-get -y install r-base libcurl4-openssl-dev gdebi-core
#sudo apt-get -y install r-cran-rjava
#sudo apt-get -y install libpq-dev
#sudo apt-get -y install libmariadbclient-dev
#sudo apt-get -y install mysql-client
#wget https://download2.rstudio.org/rstudio-server-1.1.383-amd64.deb -P /tmp

#cd /usr/local/lib/R && sudo chmod o+w site-library
#cd /vagrant && sudo Rscript Packages.R
#cd /vagrant && pip install -r requirements.txt

#sudo gdebi -n /tmp/rstudio-server-1.1.383-amd64.deb
