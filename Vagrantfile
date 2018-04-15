# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "ubuntu/trusty64"

    config.vm.provider "virtualbox" do |v|
        v.memory = 2048
        v.cpus = 1

    end

    config.vm.provision :shell, :path => "vagrant_init.sh"
    # R Studio Server port forwarding
    config.vm.network :forwarded_port, guest: 8787, host: 1234
    config.vm.network :forwarded_port, guest: 8100, host: 8100

	#config.vm.synced_folder "/Users/EMH_TRADE/Dropbox (emhTrade)", "/Dropbox"

end
