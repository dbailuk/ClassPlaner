#!/bin/bash
flask db upgrade

exec gunicorn run:app
