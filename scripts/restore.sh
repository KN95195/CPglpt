#!/usr/bin/env sh
set -eu
[ $# -eq 1 ] || { echo "Usage: $0 backups/postgres-YYYYMMDD-HHMMSS.sql"; exit 2; }
db_user=${POSTGRES_USER:-haizhi_app}
db_name=${POSTGRES_DB:-haizhi_hub}
cat "$1" | docker exec -i haizhi-hub-postgres psql -U "$db_user" -d "$db_name"
echo "Database restore completed. Restore MinIO data separately after review."
