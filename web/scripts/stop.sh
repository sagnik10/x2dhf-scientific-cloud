#!/bin/bash
docker-compose -f docker-compose.prod.yml down
docker volume prune -f
echo "X2DHF SaaS stopped and cleaned."
