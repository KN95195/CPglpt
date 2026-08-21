#!/usr/bin/env sh
set -eu
stamp=$(date +%Y%m%d-%H%M%S)
backup_dir=${BACKUP_DIR:-backups}
mkdir -p "$backup_dir"
db_user=${POSTGRES_USER:-haizhi_app}
db_name=${POSTGRES_DB:-haizhi_hub}
docker exec haizhi-hub-postgres pg_dump -U "$db_user" "$db_name" > "$backup_dir/postgres-$stamp.sql"
archive_image=${ARCHIVE_IMAGE:-haizhi-hub-api:3.2}
case "$backup_dir" in
  /*) backup_host="$backup_dir" ;;
  *) backup_host="$(pwd)/$backup_dir" ;;
esac
docker run --rm --entrypoint sh -v haizhi_hub_minio_data:/source -v "$backup_host":/backup "$archive_image" -c "tar -czf /backup/minio-$stamp.tgz -C /source ."
echo "Backup created: $stamp"
