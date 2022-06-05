#! /bin/bash
source venv/bin/activate
export FLASK_APP=flaskr
export FLASK_ENV=development
pip3 install regex
flask run