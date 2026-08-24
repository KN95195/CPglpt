# Phase 2 E2E 验收报告

## 环境

- 正式地址：`http://10.1.2.1:443/`
- 镜像：`haizhi-hub-api:6.0.5-phase2-style-fix`
- Alembic：`c3d4e5f60718`
- 提交：`1c91a3a`

## 业务用例

| 用例 | 结果 | 关键证据 |
|---|---|---|
| 首页真实知识问答 | PASS | 真实算法、产品、资料来源 |
| 桥梁防撞需求解析 | PASS | 上下游各 3 公里正确解析 |
| BOM 推荐与人工编辑 | PASS | 项目 6，数量 2，人工备注 |
| 规则校验与版本 | PASS | 3/0/0，V3 不可变历史 |
| Excel 映射/预览/下载 | PASS | 模板 3、标准 XLSX 样例 |
| 资料预览/下载/发布同步 | PASS | 文档 14，PUBLISHED/CURRENT/SYNCED |
| Dify/RAG | PASS | 真实数据集检索，80/18081 可用 |
| 六大中心 | PASS | 12/12 列表与详情 |
| 价格与角色权限 | PASS | 后端字段级过滤和 403 |
| LDAP 实际销售登录 | BLOCKED | AD 返回 52e invalidCredentials |

## 响应式与浏览器

44 项页面/视口组合全部通过：1920x1080、1600x900、1440x900、1366x768。首页最终 `scrollWidth/clientWidth` 分别为 1905/1905、1585/1585、1425/1425、1351/1351。六大中心 12 条列表/详情路由全部无横向溢出，Console 为 0 error / 0 warning。

## 最终结论

当前环境中所有可执行的软件、数据、部署和回归工作已完成。由于 LDAP 实际登录依赖的外部 AD 凭据未通过认证，最终状态为 `PHASE 2 BUSINESS IMPLEMENTATION NOT READY`。

## 验收收尾

- 正式 Word 验收报告已逐页渲染，19/19 页无裁切、重叠、缺字或表格破损。
- 原资料中心异常证据图已在正式 6.0.5 环境重新采集，页面显示文档 `PUBLISHED / CURRENT / SYNCED`。
- 临时浏览器验收账号 id 15 因审计记录外键需保留，已验证精确用户名后禁用，无法继续登录。
- 临时候选容器 `haizhi-phase2-style-candidate` 已停止并保留，正式容器与回滚容器未受影响。
