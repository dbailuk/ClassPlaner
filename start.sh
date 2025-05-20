#!/bin/bash
flask db upgrade

export FLASK_APP=run.py
exec gunicorn run:app
