apt_distro: bionic
gunicorn_args: --workers 8
ini_file: production.ini
hsts_max_age: 63072000
nginx_worker_processes: auto
postgresql_version: 12
prometheus_ips: ['2607:5300:201:3100::6e77']
hostname: tildes.net
site_hostname: tildes.net
ipv6_address: '2607:5300:0203:2dd8::'
ipv6_gateway: '2607:5300:0203:2dff:ff:ff:ff:ff'
