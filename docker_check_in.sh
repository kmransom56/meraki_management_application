#!/bin/bash
# View container status
docker compose ps

# View logs
docker compose logs -f

# Stop container
docker compose down

# Restart container
docker compose restart