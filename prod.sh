#!/bin/bash
exec docker-compose -f docker-compose.yml -f prod.yml $@
