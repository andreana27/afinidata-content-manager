#!/usr/bin/env bash
dotenv run gunicorn --statsd-host=metrics.afinidata.com:8125 --statsd-prefix=afinidata.cm2 -w 4 content_manager.wsgi

