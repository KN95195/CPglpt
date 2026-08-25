# Phase 2 UI Polish 回滚方案

- 切换前备份：`/data/haizhi-product-hub/backups/20260824-ui-polish-predeploy`
- 即时回滚容器：`haizhi-hub-api-v605-uirollback-20260825`
- 回滚镜像：`haizhi-hub-api:6.0.5-phase2-style-fix`
- 正式镜像：`haizhi-hub-api:6.1.0-ui-polish`
- 数据库版本：未变更，保持 `c3d4e5f60718`，无需数据库回滚。

回滚时停止并重命名当前 `haizhi-hub-api`，将保留的 V6.0.5 容器恢复为正式名称后启动；网关继续通过容器名 `haizhi-hub-api` 路由。随后验证 18080 和 443 健康接口、首页静态入口及 Moodle 子路径。网关配置备份位于上述备份目录。
