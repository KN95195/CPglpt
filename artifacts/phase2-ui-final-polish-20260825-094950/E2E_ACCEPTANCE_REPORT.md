# Phase 2 UI & Interaction E2E 验收报告

## 环境

- 隔离候选镜像：`haizhi-hub-api:6.1.0-ui-polish-candidate-final`
- 正式镜像：`haizhi-hub-api:6.1.0-ui-polish`
- 两个镜像 ID：`sha256:45dffe7e0d2b4c23d01cf91a13eaa09928bd5d815d15952097818847cdac9bac`
- 正式数据库：Alembic `c3d4e5f60718 (head)`
- 候选数据库：隔离 PostgreSQL，未写生产数据

## 主业务 E2E

1. 首页真实知识问答“海智AI分析终端支持哪些算法？”返回结构化正文与 3 个真实产品入口：PASS。
2. 自然语言需求“上下游各3公里、4个球机、AIS融合、船名OCR、偏航预警、7×24小时”解析为桥梁防撞、上下游 3 km、球机 4 台及能力要求：PASS。
3. 创建隔离验收项目并生成“桥梁防撞标准方案”与真实 V1 BOM：PASS。
4. BOM Drawer 将数量 1 调整为 2，备注“主平台双机冗余”，显示“人工调整”：PASS。
5. 保存产生不可变 V2；补充必需产品后产生 V3；V1/V2 历史保持只读：PASS。
6. 首次校验得到 3 PASS / 0 WARNING / 1 ERROR，销售侧显示联系产品经理提示：PASS。
7. 修正后重新校验得到 4 PASS / 0 WARNING / 0 ERROR：PASS。
8. Excel 模板可视化映射显示项目单元格、BOM 明细行和 9/9 列完成：PASS。
9. Excel 效果预览展示项目、客户、BOM 行、数量、单价、小计及备注；生成 `UI交互验收项目-20260825-BOM-V3.xlsx`：PASS。
10. 资料中心显示中文业务状态、版本状态和 AI 知识状态；上传表单分组与大尺寸预览通过：PASS。

## 权限验收

- 管理员：知识管理、模板映射、资料上传入口可见：PASS。
- 销售：项目/BOM/价格可见，人工调整和校验可操作：PASS。
- 无 `PRICE_VIEW`、无 `KNOWLEDGE_MANAGE` 用户：产品详情不含价格，价格接口 HTTP 403，知识写接口 HTTP 403：PASS。
- LDAP：未修改；本轮只验证登录界面和既有认证链未被 UI 改动破坏。

## 六大中心回归

`/products`、`/products/1`、`/software`、`/software/1`、`/algorithms`、`/algorithms/1`、`/model-capabilities`、`/model-capabilities/1`、`/scenes`、`/scenes/1`、`/solutions`、`/solutions/1`：12/12 PASS；无加载错误、无页面级横向溢出、Console 0 error / 0 warning。

## 响应式回归

| 视口 | 首页 | BOM | 页面级横向溢出 |
|---|---|---|---|
| 1920×1080 | PASS | PASS | 无 |
| 1600×900 | PASS | PASS | 无 |
| 1440×900 | PASS | PASS | 无 |
| 1366×768 | PASS | PASS | 无 |

1366×768 资料中心与 Excel 效果预览：PASS。

## 正式切换回归

- 正式 API 18080：HTTP 200。
- 正式网关 443 `/api/health`：HTTP 200。
- 正式前端入口：`index-D4lSoA8j.js`。
- 正式运行：UID/GID `10001:10001`、read-only root、cap drop ALL、no-new-privileges、noexec/nosuid `/tmp`。
- Dify 端口 80：HTTP 307 到已完成认证入口；未变更 Dify。
- Moodle `/moodle/`：HTTP 200；未变更 Moodle。

最终结果：六项 Gate 全部 PASS，`PHASE 2 UI & INTERACTION ACCEPTED`。
