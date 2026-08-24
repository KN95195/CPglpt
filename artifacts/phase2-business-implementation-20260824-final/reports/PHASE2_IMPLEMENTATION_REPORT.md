# 海智产品中心 Phase 2 实施报告

## 结论

Phase 2 的 AI 问答、智能配单、项目 BOM、Excel 模板映射与导出、资料中心、Dify/RAG 集成均已开发、部署并完成业务回归。正式镜像为 `haizhi-hub-api:6.0.5-phase2-style-fix`，Alembic 为 `c3d4e5f60718`，实现提交为 `1c91a3a`。

最终业务状态为 `PHASE 2 BUSINESS IMPLEMENTATION NOT READY`。唯一业务验收阻塞是 AD 实际认证仍返回 Active Directory 子码 `52e`（凭据无效）；同时正式 HTTPS 仍缺少域名和可信证书。其余当前环境可执行项目均已完成。

## 正式地址

- 海智产品中心：`http://10.1.2.1:443/`
- Dify 正式入口：`http://10.1.2.1/`
- Dify 保留入口：`http://10.1.2.1:18081/`
- Moodle：`http://10.1.2.1:443/moodle/`

## 已交付业务闭环

- 首页知识问答：结构化业务数据优先，RAG 资料补充，输出去除模型思考内容。
- 智能配单：自然语言解析、需求确认、真实产品 BOM 推荐、规则校验、人工修改、不可变版本。
- 项目 BOM：验收项目 id 6 已保存至 V3，人工数量与备注未被规则覆盖。
- Excel：占位符模板和普通模板均支持；普通模板支持多 Sheet、单元格映射、BOM 列映射、效果预览和鉴权下载。
- 资料中心：原文件与预览衍生物分离；支持草稿、发布、当前/历史/废止和受控知识同步。
- Dify：版本 1.16.1，真实资料同步和检索通过，80 端口入口完成可回滚切换。

## 生产验证摘要

- 前端构建：PASS
- Python 编译：PASS
- 候选/正式健康检查：PASS
- 44 项响应式检查：44/44 PASS
- 六大中心列表/详情：12/12 PASS
- 浏览器 Console：0 error / 0 warning
- 正式 Excel 下载与打开：PASS
- 文档预览、原文件下载、发布同步：PASS
- Dify 80/18081 setup 状态：`finished`
- AD 真实登录：BLOCKED（`52e invalidCredentials`）

## 数据清洁

已核验并通过鉴权 API 删除唯一无意义项目 `嗯嗯嗯`（id 5）。产品 id 27 `雷达` 未被修改。正式验收项目 id 6 保留。

临时浏览器验收账号 id 15 已在精确核对用户名后禁用。该账号存在审计历史，物理删除会被数据库审计外键阻止，因此保留禁用记录以维持审计完整性。临时候选容器 `haizhi-phase2-style-candidate` 已停止。

## 证据

- 截图：`../screenshots/`
- Excel 样例：`../export-samples/桥梁防撞业务验收项目-BOM-V3-标准模板.xlsx`
- 测试模板与检查记录：`../tests/`
- Checkpoint：项目根目录 `CODEX_CHECKPOINT.md`
