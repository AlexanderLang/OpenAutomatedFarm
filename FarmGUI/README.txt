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

- start farmgui and oafd at boot

    cp ../systemd/*.service /etc/systemd/system
    systemctl daemon-reload
    systemctl enable farmgui
    systemctl enable oafd
    systemctl start farmgui
    systemctl start oafd




