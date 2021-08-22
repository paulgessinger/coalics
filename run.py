#!/usr/bin/env python3
from coalics import app
import config

app.run(host="0.0.0.0", port=config.APP_PORT)
