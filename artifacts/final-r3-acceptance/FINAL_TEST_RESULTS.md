# 海智产品中心六大知识中心最终测试结果

- Final status: `SIX CENTERS PRODUCTION READY`
- Formal URL: `http://10.1.2.1:443/`
- Application: `haizhi-hub-api:5.4-r3`
- Database: `4f6d8a2c1b90`
- Test date: `2026-08-23`

## Production

- Formal gateway health: PASS
- Hardened runtime (`10001:10001`, read-only, cap-drop ALL): PASS
- Cache-safe frontend asset `/assets/index-6JnvkW6p.js`: PASS
- Legacy port 80 unchanged: PASS

## Six Centers

- Six list routes: PASS
- Six detail routes: PASS
- CRUD and partial PATCH API: PASS
- Bidirectional relation API: PASS
- Relation Drawer target synchronization: PASS after fix
- Solution BOM API and browser no-op save: PASS
- Dirty product name `45` removed from visible data without deleting the record: PASS
- Protected product `雷达` unchanged: PASS

## Security

- Ordinary-user write denial: PASS
- `PRICE_VIEW` product payload omission: PASS
- `PRICE_VIEW` BOM unit/subtotal/total omission: PASS
- Browser console error/warn: 0

## Responsive

- Routes tested: 12
- Viewports: 1920x1080, 1600x900, 1440x900, 1366x768
- Total route/viewport checks: 48
- Horizontal overflow or load failures: 0

## Recovery

- Production-shaped isolated restore: PASS
- Downgrade `4f6d8a2c1b90 -> a2c63a4f5798`: PASS after compatibility fix
- Rollback image `4.2` health: PASS
- Re-upgrade `a2c63a4f5798 -> 4f6d8a2c1b90`: PASS
- Restored six-center counts: `15/3/10/15/5/6`; relations: `69`

## External Dependency

Trusted TLS is not configured because no domain and certificate were supplied. Port 443 currently serves HTTP for internal acceptance.
