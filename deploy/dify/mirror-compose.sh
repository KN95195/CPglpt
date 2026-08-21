#!/usr/bin/env sh
set -eu

# Dify's upstream compose references public registries directly. This helper
# rewrites them to the reachable DaoCloud mirror before pulling on the server.
compose_file=${1:-/opt/haizhi-product-hub/integrations/dify/dify-1.16.1/docker/docker-compose.yaml}
mirror=${DIFY_MIRROR:-docker.m.daocloud.io}
sed -i \
  -e "s#langgenius/#$mirror/langgenius/#g" \
  -e "s#image: postgres:#image: $mirror/library/postgres:#g" \
  -e "s#image: redis:#image: $mirror/library/redis:#g" \
  -e "s#image: nginx:#image: $mirror/library/nginx:#g" \
  -e "s#image: busybox:#image: $mirror/library/busybox:#g" \
  -e "s#image: ubuntu/squid:#image: $mirror/ubuntu/squid:#g" \
  -e "s#image: semitechnologies/weaviate:#image: $mirror/semitechnologies/weaviate:#g" \
  "$compose_file"
echo "Dify compose rewritten for $mirror"
