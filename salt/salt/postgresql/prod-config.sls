# Values from PGTune (https://pgtune.leopard.in.ua/)
{% set setting_values = {
    "max_connections": "200",
    "shared_buffers": "1GB",
    "effective_cache_size": "3GB",
    "maintenance_work_mem": "256MB",
    "checkpoint_completion_target": "0.7",
    "wal_buffers": "16MB",
    "default_statistics_target": "100",
    "random_page_cost": "1.1",
    "effective_io_concurrency": "200",
    "work_mem": "5242kB",
    "min_wal_size": "1GB",
    "max_wal_size": "4GB",
    "max_worker_processes": "2",
    "max_parallel_workers_per_gather": "1",
    "max_parallel_workers": "2",
    "max_parallel_maintenance_workers": "1",
} %}

{% for setting, value in setting_values.items() %}
postgresql-conf-set-{{ setting }}:
  file.replace:
    - name: /etc/postgresql/{{ pillar['postgresql_version'] }}/main/postgresql.conf
    - pattern: '^#?{{ setting }} = (?!{{ value }}).*$'
    - repl: '{{ setting }} = {{ value }}'
{% endfor %}
