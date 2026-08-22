# ROLLBACK PLAN

The stopped rollback container is `haizhi-hub-api-v55-uirollback-20260823`, based on `haizhi-hub-api:5.5-ui-final`. Predeploy PostgreSQL and MinIO backups remain at `/opt/haizhi-product-hub/backups/ui-final-predeploy-20260823`; checksums were verified. Rollback procedure: stop/remove the current API container, rename the retained rollback container to `haizhi-hub-api`, start it, verify `/api/health`, static bundle and Alembic revision, then retain the failed image for diagnosis. No database migration occurred in 5.5.1.
