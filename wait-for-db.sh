#!/usr/bin/env bash
host="$1"
port="$2"
timeout="${3:-30}"
echo "Waiting for $host:$port (timeout ${timeout}s)..."
start_ts=$(date +%s)
while :
do
  if nc -z "$host" "$port" >/dev/null 2>&1; then
    echo "DB is reachable"
    exit 0
  fi
  now_ts=$(date +%s)
  if [ $((now_ts - start_ts)) -ge "$timeout" ]; then
    echo "Timeout waiting for ${host}:${port}"
    exit 1
  fi
  sleep 1
done
