#!/bin/bash

die() {
        >&2 echo Fatal error "$@"
        exit 1
}


HOST=$(awk '/^hostname:/{print $2}'  salt/pillar/prod.sls)
(
        cd ansible
        ansible-playbook -i inventory bootstrap.yml -f 10
) || die "Failed to boostrap with Ansible "

rsync -av -zz tildes/tildes/ "root@$HOST:/opt/tildes" \
        || die "rsyncing /opt/tildes"
rsync -av salt/ "root@$HOST:/srv/" \
        || die "rsyncing /srv/{salt,pillar} "
rsync minion.prod "root@$HOST:/etc/salt/minion" \
        || die "rsyncing /etc/salt/minon "
rsync production.ini "root@$HOST:/opt/tildes" \
        || die "rsyncing /opt/tildes/production.ini"
#ssh "root@$HOST" salt-call --local state.apply \
#        || die "applying salt"
