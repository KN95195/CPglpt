# 数据库迁移报告

## 版本

- 数据库：PostgreSQL 16 Alpine
- 迁移前基线：`7a8c9d0e1f23`
- 当前正式版本：`c3d4e5f60718 (head)`
- Revision：`backend/migrations/versions/c3d4e5f60718_phase2_business_foundation.py`

## 新增能力

迁移增加需求版本、BOM 规则与版本、项目 BOM 版本、校验运行记录、Excel 模板/版本/导出记录、文档预览与知识同步字段，并补充项目归属与审计关系。

## 验证

- 隔离库 upgrade：PASS
- downgrade 至 `7a8c9d0e1f23`：PASS
- 再 upgrade 至 head：PASS
- 候选完整 API 验收：PASS
- 生产 `alembic current`：`c3d4e5f60718 (head)`
- 六大中心既有数据保持：PASS

## 备份

- Phase 2 正式切换前备份：`/data/haizhi-product-hub/backups/20260824-phase2-final-precutover`
- 备份包含 PostgreSQL、MinIO、运行配置、Dify PostgreSQL 和 Dify 配置卷，并记录 SHA-256。

## 回滚

完整回滚至 5.7.3 并恢复至 Phase 2 的演练已通过；标记包括 `PHASE2_FULL_ROLLBACK_573_PASS` 与 `PHASE2_AFTER_ROLLBACK_600_PASS`。
