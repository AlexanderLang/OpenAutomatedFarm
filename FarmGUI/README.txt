FarmGUI README
==================

Getting Started
---------------

- cd <directory containing this file>

- $VENV/bin/python setup.py develop

- $VENV/bin/initialize_FarmGUI_db development.ini

- $VENV/bin/pserve development.ini

Production Setup
----------------

- copy nginx configuration files to /etc:

    cp nginx/nginx.conf.example /etc/nginx/ngings.conf
    cp nginx/farmgui.conf /etc/nginx/

- restart nginx

    systemctl restart nginx

- start pserve in daemon mode

    nice -5 pserve --daemon --pid-file=pserve_5000.pid production.ini http_port=5000


