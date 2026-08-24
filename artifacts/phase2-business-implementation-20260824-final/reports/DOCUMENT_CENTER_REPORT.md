# 资料中心报告

## 功能

- 上传：PDF、图片、Word、Excel、PPT、TXT
- 原文件独立保存，不被预览衍生物覆盖
- Word/PPT 转 PDF；Excel 转只读 HTML；PDF/图片/TXT 直接预览
- 资料元数据、知识中心关联、适用型号/版本、草稿与发布状态
- 登录鉴权预览与原文件下载

## 知识治理规则

只有同时满足以下条件才允许同步 Dify：

1. `status=PUBLISHED`
2. `documentStatus=CURRENT`
3. `knowledgeEnabled=true`

历史或废止版本不作为当前优先知识源；新 CURRENT 版本发布时，旧版本转为 HISTORICAL/OUTDATED，不物理删除。

## 正式验收

- PRD DOCX 在线预览：返回派生 PDF，PASS
- 原始 DOCX 下载：字节保持，PASS
- 草稿同步阻断：PASS
- 文档 id 14 发布：PASS
- 当前状态：`PUBLISHED / CURRENT / SYNCED`
- 精确脏资料 `hz-storage-test.txt`：已删除

浏览器安全策略不允许自动化工具直接导航到受保护 blob 预览页；受鉴权的预览与下载 API 已验证，资料中心页面状态截图已保留。
