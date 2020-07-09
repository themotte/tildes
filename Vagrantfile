# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANT_CONFIG_VERSION = "2"

Vagrant.configure(VAGRANT_CONFIG_VERSION) do |config|
  # This should correspond to apt_distro in `salt/pillar`
  # Must support libvirt for travis-ci testing
  config.vm.box = "generic/ubuntu1804"

  # Main application folder
  config.vm.synced_folder "tildes/", "/opt/tildes/"

  # Mount the salt file root and pillar root
  config.vm.synced_folder "salt/salt/", "/srv/salt/"
  config.vm.synced_folder "salt/pillar/", "/srv/pillar/"

  config.vm.network "forwarded_port", guest: 443, host: 4443
  config.vm.network "forwarded_port", guest: 9090, host: 9090

  # Masterless salt provisioning
  config.vm.provision :salt do |salt|
      salt.masterless = true
      salt.minion_config = "salt/minion"
      salt.run_highstate = true
      salt.verbose = true
      salt.log_level = "info"

      salt.install_type = "stable"
      salt.version = "3000"
  end

  config.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = "1"
  end
end
