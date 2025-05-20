#!/bin/bash

flask db upgrade
flask db heads

export FLASK_APP=run.py
exec gunicorn run:app
