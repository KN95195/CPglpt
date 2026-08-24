# 回滚方案

## API/前端回滚

当前正式容器：`haizhi-hub-api` -> `haizhi-hub-api:6.0.5-phase2-style-fix`。

即时回滚点：`haizhi-hub-api-v604-stylerollback-20260824` -> `haizhi-hub-api:6.0.4-phase2-download-fix`。

操作原则：停止当前容器，保留容器和镜像；用相同环境文件、网络、18080 映射和安全参数启动 6.0.4；验证 `/api/health` 与 443 网关后再清理。不得删除 6.0.5 或数据库备份。

## 数据库回滚

优先使用 Alembic downgrade；需要全量恢复时使用 `/data/haizhi-product-hub/backups/20260824-phase2-final-precutover/haizhi-postgres.dump`。MinIO、运行配置和 Dify 数据有同批备份。完整 5.7.3 回滚和 Phase 2 恢复演练已通过。

## Dify 80 入口回滚

备份：`/data/haizhi-product-hub/backups/20260824-phase2-port80-cutover`。

回滚步骤：

1. 停止并保留 `haizhi-dify-port80`。
2. `systemctl enable haizhi-product-center`。
3. `systemctl start haizhi-product-center`。
4. 验证 80 端口和 SQLite 数据。

旧代码、`.env`、SQLite 和 systemd unit 均未删除，SHA-256 校验已通过。

## 触发条件

- 正式健康检查失败
- 443 首页或 API 不可用
- 数据迁移出现不可接受的数据损坏
- Dify 80 入口不可访问且无法在当前窗口修复

当前没有触发回滚条件。
