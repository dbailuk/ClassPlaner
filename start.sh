#!/bin/bash

flask db upgrade

export FLASK_APP=run.py
exec gunicorn \
  --bind 0.0.0.0:${PORT:-5000} \
  run:app
