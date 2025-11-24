#!/bin/bash

echo "╔═══════════════════════════════════════════════╗"
echo "║      Mini Bingo Game - Docker Player          ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

if ! docker ps | grep -q "bingo-server"; then
    echo "Server is not running. Starting server..."
    docker-compose up -d bingo-server redis
    echo "Server started! Waiting for it to be ready..."
    sleep 3
fi

echo "Starting multiplayer client..."
echo ""

docker-compose run --rm bingo-client