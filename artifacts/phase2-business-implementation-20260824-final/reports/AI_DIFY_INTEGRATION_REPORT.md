# AI 与 Dify 集成报告

## 架构

- 本地模型服务：`http://10.1.2.4:6999`
- 模型：`/model/models/Qwen3.6-27B`
- 海智 AI Gateway：鉴权、允许模型约束、响应规范化与审计
- Dify：1.16.1，OpenAI API Compatible 插件 0.0.62
- Dataset：`6b164760-8c9b-4c37-b0f7-96864d88b9c3`

## 知识问答

系统先读取六大中心结构化关系，再调用 Dify 当前有效资料。模型返回中的 `reasoning_content`、`<think>` 和已知推理泄露标记会被清理；异常时回退到确定性结构化/RAG 答案。

## 验证

- 模型发现与聊天：PASS
- Dify Provider 校验：PASS
- `/datasets/{dataset_id}/retrieve`：PASS
- 真实 PRD 文档同步与检索：PASS
- 文档 id 14：`PUBLISHED / CURRENT / SYNCED`
- 草稿禁止同步：PASS
- `海智AI分析终端支持哪些算法？`：返回真实关系数据
- `帮我找海智AI终端使用说明书`：返回受控资料来源

## 正式入口

旧版 Python/SQLite 服务已备份后停用，Dify 通过硬化代理发布到 `http://10.1.2.1/`；原 `18081` 入口保留。两个入口的 setup 状态均为 `finished`。

## 限制

Dify 控制台密码登录采用客户端公钥加密，简单 HTTP 明文密码探测会返回 `Invalid encrypted data`，不影响当前 Provider、应用调用、同步和检索结果。
