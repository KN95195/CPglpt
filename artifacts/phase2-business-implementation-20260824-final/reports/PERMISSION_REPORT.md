# 权限与安全报告

## 权限边界

- 普通用户：知识问答、六大中心只读、已发布资料查看/预览/下载；无价格、项目、BOM、Excel 导出和后台管理。
- 销售：增加项目配单、BOM 编辑和授权价格查看。
- 产品经理：知识内容管理、资料发布/同步、项目/BOM/Excel 能力和价格查看。
- 管理员：全部权限，包括用户、角色、AD 配置和规则管理。

## 安全验证

- 后端真实鉴权，不依赖前端隐藏：PASS
- 无 `PRICE_VIEW` 时产品价格不返回：PASS
- 无 `PRICE_VIEW` 时方案 BOM 单价/小计/总价不返回：PASS
- 普通用户写操作 403：PASS
- 文件下载必须登录：PASS
- 管理后台路由/API 权限：PASS
- Dify 不接收成本价、密码和 LDAP 密钥：PASS
- 正式 API 容器：UID/GID 10001、只读根、cap drop ALL、no-new-privileges、noexec/nosuid `/tmp`

## AD 状态

系统已实现管理员手动配置、启用开关、连接测试、候选用户拉取、选择确认后创建/更新用户和中文角色分配。网络、389/636、RootDSE、域名和 Base DN 已验证；实际 bind 返回 `52e invalidCredentials`，需域管理员确认 `ldapreader@hilaicloud.com` 的密码、启用、锁定和过期状态。
