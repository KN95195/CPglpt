# FINAL OBJECTIVE
Complete the official product-material import and acceptance for 海智产品中心 using the user-provided workbook and source archive, while preserving rollback capability and all previously passed platform gates. End this work item at `WAITING_FOR_PRODUCT_DATA_REVIEW` after production deployment and regression pass.

# CURRENT PHASE
PRODUCT_PLATFORM_REMEDIATION_IMPLEMENTATION

# CURRENT BUSINESS LOOP
Official source-backed catalog cleanup, product/tender parameter import, document publication, image publication, permission verification, and production acceptance.

# LAST SUCCESSFUL STEP
CANDIDATE-RUNTIME-20260919: Started isolated `haizhi-620-api` on `127.0.0.1:18091` using image `6.2.0-product-platform` and the cloned database. Health returned OK; Alembic is `d4e5f60718a1`; runtime uses UID/GID `10001:10001`, read-only root, `no-new-privileges`, capability drop `ALL`, and hardened `/tmp`.

# CURRENT STEP
PRODUCTION_FIX5_R2_DEPLOYED_POST_SWITCH_REGRESSION

# DATA PRESERVATION NOTE
- 用户已录入的正式平台信息保持不变；本轮整改包尚未上传、构建、迁移或切换到正式服务。
- 正式数据库当前未执行本轮 `d4e5f60718a1` 迁移，现有正式 schema 和数据保持原样。
- 已创建发布前数据库备份：`/data/haizhi-product-hub/backups/20260918-product-platform-62/predeploy.sql`。
- 只有在发布包成功上传、候选环境完整回归通过、迁移前再次核对备份后，才允许进行正式切换；失败时回滚到现有 `haizhi-hub-api:6.1.8-parameter-persistence`。

# NEXT EXACT STEP
POST_SWITCH_BROWSER_AND_AUTHENTICATED_REGRESSION

# CANDIDATE FIX5-R2 STATUS (2026-09-21)
- Applied overlay2 to the isolated fix5 release; relation metadata now accepts `version`, and document acceptance explicitly publishes uploads before visibility/download checks.
- Built immutable images `haizhi-hub-frontend:6.2.0-fix5-r2` and `haizhi-hub-api:6.2.0-product-platform-fix5-r2`.
- Replaced only isolated `haizhi-620-api` on `127.0.0.1:18091`; previous candidate retained as `haizhi-620-api-fix5-rollback-20260921`. Formal service/database remain untouched.
- Health returned `{"status":"ok"}` after startup; container remains UID/GID 10001:10001, read-only root, no-new-privileges, CapDrop ALL, hardened tmpfs.
- Candidate results: `live_product_acceptance` PASS; `live_v3_knowledge_acceptance` PASS; `inline_assets_acceptance` PASS (image upload, generic document, reader preview/download denial, manager download); `live_documents_tender_acceptance` could not run because the extracted release lacks its imported `live_catalog_acceptance` module; `live_price_acceptance` has the same missing-module dependency; BOM suite remains to be run.
- The remaining price/BOM/document-tender scripts import `live_catalog_acceptance.py`, which is absent from the extracted release; their current errors are test-harness dependency errors, not product assertions. Do not promote until this missing test module is supplied or the suites are run via an equivalent containerized harness.
- Formal service was switched to fix5-r2 only after a fresh database dump; Dify/port services were not changed. Existing formal database was reused in place.

# PRODUCTION SWITCH (2026-09-21)
- Backup: `/data/haizhi-product-hub/backups/20260921-formal-pre-switch/predeploy.sql`, 6,174,466 bytes, SHA-256 `3fa76d69f64f7e7673e98ea183ad33c427df40c611c60c00edc89a3dc884ef3e`.
- Previous production container retained as `haizhi-hub-api-6.1.8-rollback-20260921`.
- New production `haizhi-hub-api` uses `haizhi-hub-api:6.2.0-product-platform-fix5-r2`, port `18080`, same production `haizhi_hub` database, no data import or destructive cleanup.
- Post-switch health returned `status: ok`; all six unauthenticated list endpoints returned expected `401` responses; gateway remained up.

# COMPLETED STEPS
- PRODUCT-PLATFORM-620-FIX-011: User uploaded fix4 under the JumpServer `fabu` folder; server-side `find` located the exact archive at `/tmp/haizhi-product-platform-6.2.0-source-fix4.tar.gz`. Size 8,763,475 and SHA-256 `82c94432306d625d9db614e6cb33338650b5df761066dda3cefe764f57c91fe1`; archive path safety passed. Extracted to `/opt/haizhi-product-hub/releases/6.2.0-20260921-fix4`. Frontend-inclusive Docker build exposed an nginx-only image, so the immutable candidate was rebuilt safely from the previously verified fix3 API image plus fix4 `app/main.py`; image ID `sha256:e56a406ba0114aa5a04ba1d50f6e82f8a9554ca19381502807df6f9bf63e85d8`. Candidate `haizhi-620-api` restarted on localhost 18091 with schema `d4e5f60718a1`, UID/GID 10001:10001, read-only root, no-new-privileges, CapDrop ALL, hardened tmpfs. `/api/health` returned HTTP 200; formal services and database remain untouched.
- PRODUCT-PLATFORM-620-FIX-012: Candidate-only acceptance preparation completed. The isolated candidate users `admin` and `sales` were assigned a temporary test password inside the cloned candidate database only; no formal database was modified. Acceptance scripts are present under the extracted fix4 release. Full candidate suites remain the next required gate before any formal migration or service cutover.
- PRODUCT-PLATFORM-620-FIX-013: Fixed two product-detail persistence edge cases in the source: nullable `last_verified_at` no longer crashes product detail reads, and product updates return the permission-filtered detail DTO with the current user so PRICE_VIEW managers receive the price payload after saving. `compileall` and `git diff --check` passed; formal runtime remains unchanged.
- PRODUCT-PLATFORM-620-FIX-014: Added server-side `q` search filtering to the shared catalog endpoint used by software, algorithm, model-capability, scene, and solution centers (name plus available code/version/summary/description fields). This closes the non-product center search gap; compile and diff checks passed. Formal runtime remains unchanged.
- PRODUCT-PLATFORM-620-FIX-015: Fixed relation CRUD fidelity: the relation drawer's Chinese relation type is now persisted and returned, duplicate detection includes relation type, and all UI-supported metadata (`requirementLevel`, `solutionLevel`, `recommended`, `condition`, etc.) is accepted when editing. Compile and diff checks passed; formal runtime remains unchanged.
- PRODUCT-PLATFORM-620-FIX-016: Relation editing now also persists a changed relation type (not just metadata) and returns it from the update endpoint. Compile and diff checks passed; formal runtime remains unchanged.
- PRODUCT-PLATFORM-620-FIX-017: Fixed a critical non-product CRUD route mismatch. The Vue create/edit/delete flows for software, algorithms, model capabilities, scenes and solutions now use `/api/admin/catalog/{kind}` while detail reads remain canonical `/api/{kind}`. Catalog request models now normalize the camelCase fields emitted by the UI. Python compilation, full Vue production build and diff check passed. Formal runtime remains unchanged.
- PRODUCT-PLATFORM-620-FIX-010: Rechecked the authenticated JumpServer SFTP root after the user reported fix4 upload completion. After refresh, the server directory still contains 331 items but no fix4 archive (exact filename, fix4, and platform searches all returned no match). No candidate build, migration, container replacement, or production change was performed.
- PRODUCT-PLATFORM-620-FIX-009: Rechecked the JumpServer SFTP staging directory and confirmed the required `haizhi-product-platform-6.2.0-source-fix4.tar.gz` is still absent; only `fix3` and the original package are present. Repeated semantic, coordinate, keyboard, and file-chooser upload attempts through the authenticated file manager did not open the chooser, and fresh authenticated JumpServer Web CLI connection attempts did not advance past the CONNECT dialog. Local fix4 remains verified at 8,763,475 bytes with SHA-256 `82c94432306d625d9db614e6cb33338650b5df761066dda3cefe764f57c91fe1`. Production `6.1.8`, production database, and candidate database/runtime were not changed.
- PRODUCT-PLATFORM-620-FIX-008: Candidate core regression reached product create/search/detail after the `product_code` repair, then exposed a second real compatibility defect: the canonical product detail handler omitted the legacy `capabilities` collection expected by the currently shipped product detail component and live acceptance. Added the legacy capability collection to canonical detail output while retaining modern `relations`; production was not changed.
- PRODUCT-PLATFORM-620-FIX-007: Recreated only isolated `haizhi-620-api` from `haizhi-hub-api:6.2.0-product-platform-fix3`, preserving its environment without displaying secrets and retaining stopped rollback `haizhi-620-api-prefx-fix3-20260919-220456`. Candidate health passed at `127.0.0.1:18091`; Alembic is `d4e5f60718a1`; UID/GID `10001:10001`, read-only root, `no-new-privileges`, capability drop `ALL`, hardened `/tmp`, and localhost-only port binding all verified. Production remains unchanged.
- PRODUCT-PLATFORM-620-FIX-006: Validated the uploaded archive contains no absolute or parent-traversal paths, extracted it to `/opt/haizhi-product-hub/releases/6.2.0-20260919-fix3`, verified embedded application/test fix markers, and built immutable image `haizhi-hub-api:6.2.0-product-platform-fix3` (`sha256:9f31e15cb53a0984cd1209b2a329e324bfe2139cc96f1c790d634639e31f1642`). Production runtime and database remain unchanged.
- PRODUCT-PLATFORM-620-FIX-005: User uploaded `haizhi-product-platform-6.2.0-source-fix3.tar.gz` through the approved JumpServer SFTP surface. Server-side verification at `/tmp/haizhi-product-platform-6.2.0-source-fix3.tar.gz` matched the local artifact exactly: 8,763,331 bytes and SHA-256 `682053c1c31e92d1f2808e859ebd3c0460d9e57f13163c114b8d310847444f77`. Production runtime and database remain unchanged.
- PRODUCT-PLATFORM-620-FIX-004: Hardened compatibility product creation before candidate deployment: trims and normalizes `model_code`, returns HTTP 409 for duplicate model codes instead of a database 500, and extends live acceptance to cover empty-summary creation plus duplicate-model rejection. `py_compile` and `git diff --check` passed. Rebuilt clean 122-entry artifact `artifacts/haizhi-product-platform-6.2.0-source-fix3.tar.gz`; size 8,763,331 bytes; SHA-256 `682053c1c31e92d1f2808e859ebd3c0460d9e57f13163c114b8d310847444f77`; embedded application and regression-test markers verified. Production runtime and data remain unchanged.
- PRODUCT-PLATFORM-620-FIX-001: Fixed the legacy `/api/admin/products` and `/api/products` create handler to derive a non-empty unique `product_code` from `model_code`, return `productCode` in compatibility DTOs, and assert create/detail persistence in the live product acceptance suite. No production runtime or database was changed.
- PRODUCT-PLATFORM-620-FIX-002: `py_compile` passed for the fixed application and acceptance script, and `git diff --check` passed. Broad local unit discovery could not load optional runtime dependencies (`httpx`, `python-docx`, backend package path) in the workstation Python; this is an environment-only test-loader failure and the containerized candidate remains the authoritative regression environment.
- PRODUCT-PLATFORM-620-FIX-003: Rebuilt `artifacts/haizhi-product-platform-6.2.0-source.tar.gz` with 166 source entries, excluding caches/build intermediates; verified embedded application and live-acceptance fixes. New artifact size is 8,812,043 bytes and SHA-256 is `d2d090446f756a9fa19d7a91751762c0eb3b76a35221f5f9dbaa9723d35512ce`. Preserved the previous artifact as `haizhi-product-platform-6.2.0-source-prefx-20260919.tar.gz`.
- MATERIAL-ACCEPTANCE-20260826: Built and deployed `haizhi-hub-api:6.1.6-official-materials`; candidate restart stability passed (`RESTART_STABILITY_PASS`) and the formal production container remained healthy after promotion.
- MATERIAL-IMPORT-20260826: Imported and published all 26 relevant official materials (25 files extracted from the official archive plus the master configuration workbook). Existing unrelated document id 14 was marked `DRAFT/OBSOLETE`; unrelated catalog records were reversibly archived rather than physically deleted.
- MATERIAL-DATA-20260826: Active production inventory is 3 products, 5 software records, 4 algorithms, 2 model capabilities, and 5 scenes. Unsupported placeholder variants were removed from active display. Official primary models are `HS-FCS157J1`, `HB-PD12S25`, and `HS-PL8ZTG3`.
- MATERIAL-TENDER-20260826: Imported source-backed tender parameters: 海智AI分析终端 18, 岸海船舶检测终端 29, 蓬莱智算一体机 12. Official algorithm codes are `HA-SIT25V2`, `HA-SNO25V2`, `HA-SHD25V2`, and `HA-RFS25V2`.
- MATERIAL-MEDIA-20260826: Uploaded 7 knowledge images; all three official products have main images and all five scenes have cover images. Added `.xls` preview support and verified all three tender spreadsheet previews return HTTP 200.
- MATERIAL-PERMISSIONS-20260826: Reader price keys are absent; reader document preview returns 200; reader download returns 403; administrator download returns 200. Temporary browser acceptance account id 16 was disabled after testing.
- MATERIAL-ROLLBACK-20260826: Verified database/MinIO/source rollback backup at `/data/haizhi-product-hub/backups/20260826-102616-official-material-import`; preserved rollback containers and archived data for reversible recovery.
- MATERIAL-DRY-RUN-20260826: Server-side RAR extraction passed with `All OK`; 25 source files plus `file-manifest.txt` are under `/opt/haizhi-product-hub/import/materials-20260826-103833` (396 MB). Production inventory CSVs and `dry-run-sha256.txt` were generated in the same directory: 19 product rows, 8 software rows, 14 algorithm rows, 17 capability rows, 10 scene rows, and 1 existing document row including headers.
- MATERIAL-BACKUP-20260826: Production PostgreSQL role/database discovery passed (`haizhi_app` / `haizhi_hub`). Backed up the 12 MB database, 6.0 MB MinIO volume, uploaded workbook, and 394,162,421-byte RAR at `/data/haizhi-product-hub/backups/20260826-102616-official-material-import`; all artifacts are non-empty and recorded in `SHA256SUMS`. No production catalog or document mutation occurred.
- MATERIAL-ANALYSIS-20260826: Received and extracted `核心产品标准化材料-260818同步.rar` to local staging `D:\haizhi-materials-260818` (25 files: product brochures/specifications, pricing workbooks, tender parameter sheets, PPT/DOCX collateral, certificates, and scene/platform brochures). Cross-checked against the supplied configuration workbook: source groups are 岸海船舶检测终端 (HB-PD12S25, HB-SD23S35, HB-SD50S30, HS-RAB32), 海智AI分析终端 (HS-FCS157J1, HS-GCS020A1), 蓬莱智算一体机 (HS-PL8ZTG3 variants), five software/application products, four licensed algorithms, five scenes, and two model capability metric sets. Existing idempotent importer `backend/app/material_import.py` and `official_material_2026.json` cover the structured catalog; binary documents still require transfer to the server before upload and association.
- OPS-PORT-SWAP-20260825: External validation passed for business `http://10.1.2.1/` (200), Moodle `http://10.1.2.1/moodle/` (200), Dify setup `http://10.1.2.1:443/console/api/setup` (200, finished), and Dify administrator login (200 with authentication cookies). Backup: `/data/haizhi-product-hub/backups/20260825-215842-business80-dify443`; retired rollback container: `haizhi-dify-port80-retired-20260825-223319`.
- UI-POLISH-D7: Created final report/evidence directory `artifacts/phase2-ui-final-polish-20260825-094950`, verified 28 screenshots and required reports, and packaged `phase2-ui-final-polish-20260825-094950.zip` with SHA-256 `8eb35e2c4ce784855fe6a3fa96d32e7092ac4312ea7bd4b137bab11fe377b8d2`.
- UI-POLISH-D4: Browser-tested the candidate home knowledge portal and structured AI answer, three-step project requirement analysis/recommendation, project lifecycle and tabs, three-column BOM editor, row Drawer/manual-edit tag, immutable V1/V2/V3 history, ERROR then corrected PASS validation, large Excel effect preview/generation, six-step template mapping, document upload form/large preview, and four responsive viewports. Required screenshots are under `artifacts/phase2-ui-final-polish-20260825-094950/screenshots`.
- UI-POLISH-D4-REGRESSION: Six-center list/detail routes passed 12/12 at 1440x900 with no page error or horizontal overflow. Candidate console regression recorded zero errors and zero warnings.
- UI-POLISH-D4-PERMISSION: Administrator and sales UI states passed; a no-`PRICE_VIEW`/no-`KNOWLEDGE_MANAGE` account received no product price payload, HTTP 403 on price endpoint, and HTTP 403 on knowledge write.
- UI-POLISH-D3: Deployed immutable isolated candidate `haizhi-hub-api:6.1.0-ui-polish-candidate-final` against isolated PostgreSQL at Alembic `c3d4e5f60718`; candidate health passed through the local acceptance proxy without formal cutover.
- UI-POLISH-D2: Created production UI pre-deployment backup `/data/haizhi-product-hub/backups/20260824-ui-polish-predeploy` and preserved the formal `6.0.5` runtime unchanged during candidate acceptance.
- UI-POLISH-D1: Productized the real home AI portal, structured AI answer sources, three-step intelligent configuration, project header/lifecycle/tabs, three-column BOM editor with Drawer/manual-diff/ordering, detailed validation/override UI, six-step visual Excel mapping, large export preview, and document center list/upload/in-page preview while preserving APIs, permissions, immutable BOM versions, price isolation, and Dify/LDAP scope.
- UI-POLISH-D1-BUILD: `npm run build` PASS; generated `index-D4lSoA8j.js` and `index-DlnbK5He.css`.
- PHASE2-IMPL-012B: Packaged `phase2-business-implementation-20260824-final.zip` with 80 entries, verified required Word/XLSX/manifest entries, excluded generated dependency caches, and verified SHA-256 `b63603cb04854d2bb4b1d8a0da0b576e2f2e5328c433798b5fa61b2df6b41291`.
- PHASE2-IMPL-012: Created 9/9 required Markdown reports and `海智产品中心_Phase2业务实施验收报告.docx`; exported the report to PDF, rasterized and visually inspected all 19 pages, fixed oversized image scaling, replaced the malformed document-center screenshot from the live 6.0.5 page, disabled the exact temporary acceptance account id 15 after physical deletion was correctly prevented by retained audit references, stopped `haizhi-phase2-style-candidate`, and reset browser viewport state.
- PHASE2-IMPL-011J: Built candidate `6.0.5`, passed candidate health/security/style checks, retained stopped rollback container `haizhi-hub-api-v604-stylerollback-20260824`, and deployed the same immutable image with UID/GID `10001:10001`, read-only root, capability drop `ALL`, `no-new-privileges`, and noexec/nosuid `/tmp`. Formal direct and 443 health, CSS scope, and Alembic `c3d4e5f60718` passed.
- PHASE2-IMPL-011I: Backed up the legacy port-80 service code, SQLite database, environment file, and systemd unit with verified SHA-256 at `/data/haizhi-product-hub/backups/20260824-phase2-port80-cutover`; disabled the legacy unit without deleting files; published Dify through hardened `haizhi-dify-port80`; verified browser title/login UI and `setup=finished` on ports 80 and 18081 while port 443 remained healthy.
- PHASE2-IMPL-011H: Production project `桥梁防撞业务验收项目-20260824` (id 6) passed structured parsing for `上下游各3公里`, real BOM recommendation, quantity/manual-note adjustment, 3/0/0 validation, immutable V2/V3 history, visual Excel mapping, effect preview, authenticated XLSX download, and workbook content/style inspection. Published document id 14 is `PUBLISHED`, `CURRENT`, `knowledgeEnabled=true`, and `knowledgeStatus=SYNCED`; draft synchronization denial and authenticated preview/original download passed.
- PHASE2-IMPL-011G: Real in-app-browser viewport scan passed all tested non-home Phase 2 routes. Homepage passed 1920x1080 but failed 1600x900, 1440x900, and 1366x768 because production JS uses `data-v-fb4feb6a` while its loaded stylesheet contains the stale `data-v-780e4be3` Phase2Workspace selectors. A clean local `npm run build` emits matching JS/CSS scope ids and stylesheet `index-D418WcGz.css`; root cause is a mismatched production asset package, not intended layout geometry.
- PHASE2-IMPL-011F: Created and visually verified placeholder and ordinary Excel templates, uploaded both to production, completed ordinary-template visual cell/BOM mapping, and fixed authenticated final XLSX download. Passed `PHASE2_TEMPLATE_UPLOAD_PASS`, `PHASE2_DOWNLOAD_FIX_CANDIDATE_PASS`, `PHASE2_DOWNLOAD_FIX_FORMAL_PASS`, and `PHASE2_DOWNLOAD_FIX_GATEWAY_PASS`. Formal image is `haizhi-hub-api:6.0.4-phase2-download-fix`; stopped rollback container is `haizhi-hub-api-v603-downloadrollback-20260824`.
- PHASE2-IMPL-011E: Replaced browser-incompatible cloning of the reactive BOM API payload, built the production frontend, published entry `index--Wk1AOS9.js`, and passed `PHASE2_FRONTEND_FIX_CANDIDATE_PASS`, `PHASE2_FRONTEND_FIX_FORMAL_PASS`, and `PHASE2_FRONTEND_FIX_GATEWAY_PASS`. Formal image is `haizhi-hub-api:6.0.3-phase2-browser-fix`; stopped rollback container is `haizhi-hub-api-v602-browserrollback-20260824`.
- PHASE2-IMPL-011D: Added `parse_requirement_text` shared-distance semantics for `上下游各N公里`, preserved separate upstream/downstream parsing, added two regression cases, and passed markers `PHASE2_PARSER_UNIT_PASS`, `PHASE2_PARSER_LIVE_CANDIDATE_PASS`, `PHASE2_PARSER_CANDIDATE_HEALTH_PASS`, `PHASE2_PARSER_FORMAL_HEALTH_PASS`, and `PHASE2_PARSER_FORMAL_GATEWAY_PASS`. Formal image is `haizhi-hub-api:6.0.2-phase2-parser`; stopped rollback container is `haizhi-hub-api-v601-parserrollback-20260824`.
- PHASE2-IMPL-011C: Added a system instruction that permits only concise Chinese final answers, ignores `reasoning_content`, strips `<think>` blocks, extracts explicit final-answer sections, and falls back to deterministic structured/RAG facts whenever known reasoning-leak markers appear. Unit marker: `Ran 4 tests ... OK`. Live candidate markers: status 200, answer length 166, `PRIVATE_REASONING False`, `HAS_ALGORITHM True`. Formal image is `haizhi-hub-api:6.0.1-phase2-ai-output`; rollback container `haizhi-hub-api-v600-phase2-airollback-20260824` is retained.
- PHASE2-IMPL-011B: Marker `PHASE2_UI_PERMISSION_DOCUMENT_ACCEPTANCE_PASS 17` verified dashboard role scoping, route/API denial, metadata-first document publish, authenticated preview/download, frontend bundle markers, and cleanup. Marker `PHASE2_SIX_CENTER_PRICE_VIEW_REGRESSION_PASS 19,8,14,17,10,6` verified all six center list/detail APIs, read-only write denial, project access denial, product price omission, price endpoint 403, solution BOM monetary omission, and cleanup.
- PHASE2-IMPL-011A: Dify 1.16.1 setup remains `finished`; Moodle direct/gateway probes returned 303/200; formal Dify retrieval returned one real record and marker `DIFY_RETRIEVAL_MARKER True`; `/api/ai/chat` returned HTTP 200 with a 2,599-character answer; formal health on 18080 and 443 passed after the runtime-only Dify configuration correction. The prior runtime env was preserved at `/opt/haizhi-product-hub/.runtime.env.pre-phase2-dify-20260824`, and stopped rollback container `haizhi-hub-api-v600-pre-dify-runtime-20260824` was retained.
- PHASE2-IMPL-010D: Passed markers `PHASE2_FULL_ROLLBACK_573_PASS`, `PHASE2_FULL_ROLLBACK_GATEWAY_PASS`, `PHASE2_AFTER_ROLLBACK_600_PASS`, and `PHASE2_ROLLBACK_RESTORE_COMPLETE`. Final Alembic output is `c3d4e5f60718 (head)`; production is back on Phase 2 after the rollback test.
- PHASE2-IMPL-010B: Production Alembic reported `c3d4e5f60718 (head)`; formal direct port 18080 and gateway port 443 health passed; frontend entry is `index-DYEYy9ZP.js`; formal runtime retains UID/GID `10001:10001`, read-only root filesystem, capability drop `ALL`, `no-new-privileges`, and hardened `/tmp`; rollback container is `haizhi-hub-api-v573-phase2-rollback-20260824`. Isolated formal marker `PHASE2_UI_PERMISSION_DOCUMENT_ACCEPTANCE_PASS` passed with cleanup.
- PHASE2-IMPL-010A: Generated `haizhi-postgres.dump`, `haizhi-minio.tgz`, `haizhi-runtime-config.tgz`, `dify-postgres.dump`, and `dify-config-volumes.tgz`; recorded their verified SHA-256 values in `SHA256SUMS`. No production service or data was changed during backup.
- PHASE2-IMPL-009D: Deployed candidate frontend entry `index-DYEYy9ZP.js`; marker `PHASE2_UI_PERMISSION_DOCUMENT_ACCEPTANCE_PASS` verified homepage aggregates, read-only route/API denial, sales project visibility, metadata-first document draft/edit/publish, disabled-RAG rejection, authenticated preview/download, and cleanup. Restored the isolated candidate database, upgraded to `c3d4e5f60718`, replaced an invalid minimal-PDF test fixture with a valid ReportLab PDF, then passed `PHASE2_CANDIDATE_API_ACCEPTANCE_PASS` with project 6, two immutable BOM versions, Excel SHA-256 `554d0e1ecd72eb392970df47f8e502c6ea378638c59bcfabfc5d257f1c453507`, document 16, and migration `c3d4e5f60718`.
- PHASE2-IMPL-009C: Added visible direct-route access denial in addition to backend 403 enforcement, permission-aware document navigation, role label correction for sales, editable document metadata, explicit publish without forced RAG enrollment, and knowledge synchronization only when the document is enabled. `npm run build` passed with `index-DYEYy9ZP.js` and `index-Br7JOFwG.css`.
- PHASE2-IMPL-009B: Added homepage counts, core products, common scenes, role-scoped recent projects, recent updates, and popular model capabilities; replaced unauthenticated AI source anchors with bearer-token document access; localized requirement keys, BOM rule types, validation outcomes, and document states; hid BOM prices without `PRICE_VIEW`; added category, version, description, relation, applicable model/version, and AI-knowledge controls before upload. `npm run build` passed with `index-B42W5yBs.js` and `index-CzF39Re7.css`.
- PHASE2-IMPL-009A: Added real homepage aggregate data to `/api/dashboard`, kept recent project configuration hidden without `BOM_VIEW`, scoped sales projects to their owner, and corrected clean-bootstrap role/permission definitions for documents, projects/BOM, prices, costs, and administration. `py_compile` and `git diff --check` passed.
- PHASE2-IMPL-008: Added multi-sheet cell metadata to template analysis, click-to-map project fields, structured BOM field mapping, coordinate/sheet validation, manual mapping application during workbook rendering, generated read-only HTML effect preview, export data adjustment saved as a new immutable BOM version, full BOM version history, authenticated document preview/download actions, and candidate frontend bundle `index-Da_32jig.js`. Candidate marker `EXCEL_VISUAL_MAPPING_CANDIDATE_ACCEPTANCE_PASS 3 3` verified two-sheet analysis, manual cells, BOM expansion, merged cells, freeze panes, style retention, HTML preview, final XLSX content, and cleanup.
- PHASE2-IMPL-007: Added `document_preview.py` and preview dependencies; DOCX and PPTX derive PDF, XLSX/XLSM derive read-only HTML, PDF/images/TXT remain direct; preview objects use separate MinIO keys and original downloads remain byte-identical. Unit suites passed `4 + 4`; live candidate marker `DOCUMENT_PREVIEW_CANDIDATE_ACCEPTANCE_PASS [18, 19, 20]` verified upload, READY state, preview media/content, SHA-256-identical original download, and cleanup.
- PHASE2-IMPL-006: Added normalized `/datasets/{dataset_id}/retrieve` support and unit coverage (`Ran 4 tests ... OK`); rebuilt immutable candidate `haizhi-hub-api:6.0.0-phase2-aiqa`; candidate health passed; `/api/ai/chat` returned governed local document source id 17, `ANSWER_LEN 2474`, `HAS_RAG_TERMS True`, and `CONFIG_INTENT True` for the real bridge-collision query.
- PHASE2-IMPL-005: Backed up Dify `.env` and Compose configuration at `/data/haizhi-product-hub/backups/20260824-053921-dify-celery-config`; corrected `CELERY_BROKER_URL` to the URL-encoded current Redis password; recreated only `api`, `worker`, and `worker_beat`; verified `BROKER_PING_OK`; reloaded Dify Nginx; synchronized candidate document 17 as Dify document `0ea2cdaf-b4f4-44bc-9247-363753b06e40`; and passed real retrieval with `RETRIEVE_STATUS 200`, one record, and `MARKER_MATCH True` for `桥梁防撞/AIS/船名OCR/偏航预警`.
- PHASE2-IMPL-004: Candidate acceptance passed on `haizhi-phase2-api` at `127.0.0.1:18089` using an isolated PostgreSQL restored from the verified production snapshot. Marker payload recorded project id 6, two immutable BOM versions, Excel SHA-256 `5b3ed0fe828709b08351b38a7ac130fe23bf25f81f88d49aafcebbf5722783bd`, document id 16, and migration `c3d4e5f60718`.
- PHASE2-IMPL-003: Fixed candidate-discovered role and download defects: sales now receives `BOM_EDIT` and `PRICE_VIEW` through the reversible migration; product-manager override checks use the actual `product_admin` role code; Chinese Excel download names are RFC-compatible percent-encoded; the acceptance suite creates and cleans an isolated true read-only role/user.
- PHASE2-IMPL-002: Added the reversible `c3d4e5f60718` schema for requirement, rule, BOM, validation, Excel export, document preview, and knowledge-sync versioning; isolated upgrade, downgrade to `7a8c9d0e1f23`, and re-upgrade passed.
- PHASE2-IMPL-001: Established branch `codex/phase2-business-implementation`, local build baseline, candidate staging directory `/tmp/haizhi-phase2-candidate-20260824-0020`, verified production snapshot, candidate image `haizhi-hub-api:6.0.0-phase2-runtime`, isolated PostgreSQL, and localhost candidate port 18089 without changing production.
- PHASE2-R2-DESIGN-006: Created and extraction-tested `phase2-business-design-r2-review-20260823-225023.zip`; the expanded package contains 9 R2 PNG mockups, 6 annotated PNGs, 12 Markdown documents, and `PHASE2_FIELD_DICTIONARY_R2.xlsx`.
- PHASE2-R2-DESIGN-005: Incrementally edited the R1 workbook with artifact-tool, added `AIKnowledgeQA`, updated the 10 requested sheets, rendered and visually inspected all 15 sheets, inspected the Document key range, and confirmed zero formula-error matches.
- PHASE2-R2-DESIGN-004: Rendered 7 updated and 2 new 1600x900 mockups, corrected BOM editor clipping, generated 6 annotated review pages, and verified all 15 PNG outputs at exact dimensions with no banned UI names.
- PHASE2-R2-DESIGN-003: Froze homepage, AI knowledge Q&A, structured-first knowledge, document-to-Dify synchronization, requirement/rule/validation versions, manual-BOM precedence, ERROR override, role-price, Excel mapping/preview, and Dify-entry decisions; recorded all 14 unchanged R1 mockups.
- PHASE2-R2-DESIGN-002: Completed R2 A-L self-check with all items PASS and confirmed no formal runtime, database, migration, Dify or port-80 changes.
- PHASE2-DESIGN-006: Created `phase2-business-design-review-20260823-213515/` and verified its matching ZIP by full extraction: 21 core PNGs, 7 annotated PNGs, 14 required Markdown design documents, `REVIEW_INDEX.md`, and `data/PHASE2_FIELD_DICTIONARY.xlsx` are present.
- PHASE2-DESIGN-005: Built `PHASE2_FIELD_DICTIONARY.xlsx` with Home, AIConfigurator, AIRequirement, BomEditor, BomRule, Project, ProjectBom, BomVersion, ExcelTemplate, ExportPreview, ExportRecord, Document, DocumentRelation, and DifyConfig sheets; rendered every sheet, visually inspected all renders, inspected the BomEditor key range, and confirmed zero formula-error matches.
- PHASE2-DESIGN-004: Rendered 21 high-fidelity 1600x900 business workflow pages and 7 numbered annotated pages; visually checked the homepage, BOM editor, export preview, document preview and all workbook sheet renders; all 28 core PNGs passed exact dimension validation.
- PHASE2-DESIGN-003: Completed the Phase 2 flow, UI, field mapping, current-to-target, data model, API, BOM rule, Excel template, document center, Dify, port 80, future implementation and open-question specifications without changing production implementation.
- PHASE2-DESIGN-002: Recorded the read-only baseline: local branch `feature/knowledge-centers-v3`, commit `1023e9a2112c7eb8292a4c0ec9a58f7a752fa21a`, production Alembic `7a8c9d0e1f23`, API image `haizhi-hub-api:5.7.3-ad-error-fix`, Dify 1.16.1 on internal 18081, Moodle on 18082 and the unchanged legacy Python 2.7 service on port 80.
- AD-CONFIG-010: Root-caused the misleading frontend JSON error to an AD exception containing `NUL`, which PostgreSQL rejected while persisting the failed sync run. Added centralized LDAP error sanitization, JSON-safe failure persistence/response, robust frontend response parsing, explicit login-domain validation/help text, isolated marker `AD_NUL_ERROR_API_REGRESSION_PASS`, formal marker `PRODUCTION_AD_ERROR_FIX_PASS`, hardened deployment `haizhi-hub-api:5.7.3-ad-error-fix`, exact assets `index-BjXLl0fX.js` / `index-NXPMhlE1.css`, and rollback container `haizhi-hub-api-v572-adconfig-rollback-20260823`.
- AD-CONFIG-008: Browser-verified the deployed System Management AD page at `http://10.1.2.1:443/`: manual enable switch, server type, LDAP/LDAPS protocol, host, port, timeout, administrator account, masked password, Base DN, login domain, user filter, Chinese default role, Connectivity Test, Save Configuration, and disabled-until-configured Manual Domain User Sync are all present and correctly laid out. Temporary browser acceptance account was deleted after validation.
- AD-CONFIG-007: Tagged and deployed immutable `haizhi-hub-api:5.7.2-ad-config-ui`, restored the prior least-privilege runtime (`10001:10001`, read-only root filesystem, capability drop ALL, no-new-privileges, hardened `/tmp`), verified frontend assets `index-4PeU9K2z.js` / `index-Bh1FNCuB.css`, formal health through ports 18080 and 443, Alembic `7a8c9d0e1f23`, empty-by-default LDAP host/Base DN, and Chinese role display names; retained stopped `haizhi-hub-api-v571-adrollback-20260823`.
- AD-CONFIG-006: Created formal PostgreSQL and MinIO backups with SHA-256 checksums at `/data/haizhi-product-hub/backups/20260823-194706-ad-config-5.7.2` before migration/deployment.
- AD-CONFIG-005: Passed isolated API acceptance marker `AD_CONFIG_API_ACCEPTANCE_PASS`: no backend LDAP defaults, incomplete enabled configuration rejected with 422, password never returned, ciphertext differs from plaintext, blank-password update preserves the encrypted secret, invalid credentials fail connectivity testing, and disabled synchronization is rejected.
- AD-CONFIG-004: Passed isolated Alembic upgrade to `7a8c9d0e1f23`, downgrade to `2f7b6c8d9e10`, and re-upgrade to head; built immutable candidate `hz:572b` with `cryptography-44.0.2` and passed candidate health.
- AD-CONFIG-003: Added persistent manual LDAP/LDAPS configuration, encrypted bind-password storage, status/save/test APIs, and explicit configuration readiness checks; no AD connection values are read from backend environment defaults.
- AD-CONFIG-002: Added the System Administration manual AD configuration form and actions while preserving the selected-only domain user approval workflow and Chinese role presentation.
- AD-APPROVAL-006: Created formal PostgreSQL backup `pre-571-20260823-181113.dump` and MinIO backup `pre-571-minio-20260823-181135.tgz`, verified checksums, migrated production to `2f7b6c8d9e10`, deployed `haizhi-hub-api:5.7.1-ad-approval`, passed health, and retained `haizhi-hub-api-v570-adrollback-20260823`.
- AD-APPROVAL-005: Passed isolated manual-approval acceptance with marker `AD_MANUAL_APPROVAL_ACCEPTANCE_PASS`: Chinese role validation, English role-name rejection, candidate batch retrieval, selected-only account creation, unselected-user exclusion, existing AD-user update after reconfirmation, and cleanup.
- AD-APPROVAL-004: Added pending directory candidate persistence and the `/api/admin/directory/sync`, `/candidates`, and `/confirm` two-step workflow; synchronization no longer directly creates or updates login accounts.
- AD-APPROVAL-003: Reworked System Administration to show an administrator candidate table with selection, per-user Chinese role assignment, and explicit confirmation; role codes and English permission codes are hidden from users.
- MSA-008: Created verified PostgreSQL/MinIO predeployment backups, deployed immutable `5.7.0-material-admin`, migrated production, imported formal materials idempotently, configured AD discovery metadata, passed formal API/RBAC/PRICE_VIEW/runtime acceptance, synchronized formal source, and retained `5.6.3` rollback.
- MSA-007: Passed a clean isolated migration downgrade/re-upgrade, material import twice, user CRUD, role CRUD, dynamic permission removal, PRICE_VIEW field omission, ordinary-user USER_MANAGE denial, AD-unconfigured failure audit, and cleanup.
- MSA-006: Fixed the nested permission dependency runtime `NameError`, the variant import uniqueness conflict, clean-database USER_MANAGE bootstrap assignment, and ORM relationship warning; rebuilt immutable candidate after each correction.
- MSA-005: Built `haizhi-hub-api:5.7.0-material-admin` from the locally compiled frontend runtime bundle after checksum-verified transfer.
- MSA-004: Added product variants and software/algorithm commercial profiles plus same-page editing, formal-material idempotent import, system administration UI, user/role/permission APIs, environment-only AD synchronization, and interface-level PRICE_VIEW filtering.
- MSA-003: Parsed and reconciled `海莱云智2026产品介绍（对外）.pdf` and `海莱云智产品配单工具表(修改0729)_2.xlsx` into the formal normalized import dataset.
- MSA-001: Completed the current schema/API/UI/RBAC/LDAP boundary audit and fixed the incremental design.
- IEA-005: Deployed immutable `haizhi-hub-api:5.6.3-inline-edit` with exact frontend bundle `index-BdlHTqbF.js`, retained stopped `5.6.2` rollback, and completed isolated/formal API, RBAC, PRICE_VIEW, asset, document, migration, runtime, port-80, and browser-rendering acceptance.
- IEA-004: Corrected inline child-record PATCH serialization so database `id` fields are not sent to strict backend DTOs; local Vue type-check/Vite build emitted all required application/vendor chunks.
- IEA-003: Added migration `6a9c2e7d4f31`, image and document object APIs, independent `DOCUMENT_DOWNLOAD` permission, role-permission update API, and isolated upgrade/downgrade/re-upgrade plus API acceptance coverage.
- UIF-008: Created the timestamped final acceptance package with 54 formal screenshots, 19 R3 reference mockups, implemented comparison evidence, eight focused test records, ten Markdown audit/report files, and a visually verified nine-page Word/PDF acceptance report. All Gates A-O pass; final status is `SIX CENTERS FINAL ACCEPTED`.
- UIF-007E: Formal browser verified Scene list/detail route, H1, sidebar active state, semantic `/assets/bridge-ship-waterway.jpg`, responsive no-overflow at all four requested viewport profiles; Product same-page edit exposed the editable form/save controls and Cancel restored read mode; browser console errors/warnings remained zero. Replaced all eight affected Scene evidence images and added Product edit evidence.
- UIF-007D: Switched formal runtime to immutable `haizhi-hub-api:5.5.1-ui-final` (`sha256:605485e91ca2...`), retained stopped rollback `haizhi-hub-api-v55-uirollback-20260823`, preserved legacy port 80, and passed formal health, exact static bundle, semantic image asset, Alembic `4f6d8a2c1b90`, hardened runtime, complete six-center API/RBAC/PRICE_VIEW/relation/BOM acceptance, cleanup, and gateway smoke.
- UIF-007C: Checksum-verified bundle transfer (`c5acd32c5decb98191ccb53cd6f4b50caf4cd7adbe10370328d03908056c4fb8`), immutable image build `haizhi-hub-api:5.5.1-ui-final` (`sha256:605485e91ca2...`), and hardened localhost candidate health/static/semantic-image checks passed on port 18086.
- UIF-007B: Frontend `vue-tsc -b && vite build`, backend Python compileall, and `git diff --check` passed after the Scene semantic-image correction; emitted bundle `index-DlJGqRh-.js` and stylesheet `index-B8tlaU7C.css`.
- UIF-007A: Replaced unsafe Scene list/detail image selection with a semantic fallback to `/assets/bridge-ship-waterway.jpg` when API data is empty or references known UI/mockup assets; formal database and Seed Data were not changed.
- UIF-006: Formal deployment to `5.5-ui-final` passed backup, rollback retention, health, runtime, migration, exact bundle, complete six-center API acceptance, count reconciliation, and legacy port-80 preservation gates.
- UIF-005B: Hardened localhost candidate passed health/static/runtime checks and complete six-center live API acceptance after the isolated `func` import repair; all temporary CRUD data was cleaned up.
- UIF-005A: Built immutable server candidate `haizhi-hub-api:5.5-ui-final` from the verified R3 base, scoped source changes, and final local frontend production bundle; formal runtime and database remained unchanged.
- UIF-004: Five center lists now expose center-specific visual cards and business metrics; no database change was required.
- UIF-003: Software, Algorithm, Model Capability, Scene, and Solution details now use separate R3 information architectures, working tabs, real normalized data, real relationships, and responsive layouts; frontend production build passed.
- UIF-002: Product Detail R3 productization build passed locally; no backend schema or production data change was required.
- UIF-001: Created the R3 implementation matrix, reproduced the route/evidence mismatch, and added the missing software dashboard metric.
- PI-012: Created `artifacts/haizhi-six-centers-production-ready-20260823.zip` with SHA-256 `C720663B49AF25CBB58FE9F68CBADA405F5906AB16952C4A4107A3C68CDC035A`; included the final 10-page Word acceptance report, final test results, checksums, and production screenshots; re-ran the frontend build and Python compileall; and marked the six-center implementation production-ready.
- PI-011: Reproduced and fixed the R3-to-legacy downgrade conflict caused by multiple relation types for one legacy relation pair; isolated downgrade to `a2c63a4f5798`, old image `4.2` health, re-upgrade to `4f6d8a2c1b90`, and recovered counts `15/3/10/15/5/6` plus 69 relations all passed. Fixed the Relation Drawer stale option list, deployed cache-safe frontend bundle `/assets/index-6JnvkW6p.js` in immutable `haizhi-hub-api:5.4-r3`, and browser-verified the correct scene object label.
- PI-010: Passed all six list and six detail routes, 48 route/viewport checks at 1920x1080, 1600x900, 1440x900, and 1366x768 with zero overflow/error, browser console error/warn count zero, Product edit, Relation Drawer metadata edit display, and Solution BOM no-op save. Cleaned dirty product name `45` by renaming it to `海智智能分析节点` and adding model/summary without deleting the record; protected product `雷达` remained untouched.
- PI-009: Created `/opt/haizhi-product-hub/backups/r3-predeploy-20260822-2130`, migrated formal PostgreSQL to `4f6d8a2c1b90`, deployed hardened immutable `haizhi-hub-api:5.1-r3` (`sha256:02c8daa46f92fcfd4fc39d1cfd07e0db489c6e6227a340906c2f0a58d1635afe`), retained rollback containers `haizhi-hub-api-v42-r3rollback-20260822` and `haizhi-hub-api-v50-r3rollback-20260822`, passed port-443 health, and passed `FORMAL_CRUD_PRICE_CLEANUP_PASS` without leaving temporary records.
- PI-008: Packaged candidate (`SHA-256 1f64298e271358135760c7801fa6836de7393923ce966ce1fbb5248a8170ebaf`), built immutable API/UI image `haizhi-hub-api:5.0-r3` (`sha256:a6d33fb784e64b48113aaf93dd7f1e1e15402be99a4f28eb2f51b13aaee55d40`), restored production snapshot checksum `b04b90206bcaa3a47cdb1bced19df8286cde8742837ad78e9b2b5b0bb9686685` into isolated PostgreSQL, upgraded it from `a2c63a4f5798` to `4f6d8a2c1b90`, started hardened read-only candidate on localhost 18084, and passed health, static asset, ordinary-user write denial, PRICE_VIEW omission, and complete R3 isolated API acceptance with cleanup. Formal runtime and DB remained unchanged.
- PI-007: Audited and removed obsolete frontend contracts/enums, verified no gradients, copied R3 visual assets into the production frontend, assigned semantic product/scene images without overwriting existing media, corrected `TIME_SERIES`, localized model/tier values, and added Software modules/version/dependency detail rendering. Frontend production build, Python compileall, and `git diff --check` pass.
- PI-006: Added full Product identity fields, gallery/tags/features/boundaries editing, grouped typed ProductDynamicParameter management, highlight selection, main gallery rendering, type-specific quick metrics, structured feature and boundary sections, and complete read-state descriptions. Frontend production build passed.
- PI-005: Replaced the generic non-product editor with center-specific frozen fields and normalized transformations: Software modules/features/versions/screenshots/database/protocols; Algorithm principle/input/output/parameters/metrics; Model types/task/I-O/test evidence/deployment/use conditions; Scene tags/conditions/pains/goals/process; Solution scene/tier/architecture/capability coverage. Frontend production build passed.
- PI-004: Completed relation type selection (`SUPPORT`, `COMMERCIALIZATION`, `RECOMMENDATION`, `COMPOSITION`, `RELATED`), constrained commercialization to Product-to-Software, rendered only backend-allowed metadata per center pair, normalized concurrency values, and added relation PATCH editing. Frontend production build passed after the change.
- PI-003: Current R3 frontend production build passed locally with `vue-tsc -b && vite build`; emitted production assets without TypeScript/Vue compilation errors. Remaining Sass import and chunk-size messages are non-blocking warnings.
- PI-002: On isolated PostgreSQL runtime on `172.20.1.7`, passed clean zero-to-`4f6d8a2c1b90` migration, downgrade to `a2c63a4f5798`, re-upgrade, application import/route precedence, semantic seed initialization, minimum six-center counts, normalized child and relation counts, no deprecated product types, six-center CRUD, partial PATCH, reader write denial, PRICE_VIEW omission, bidirectional relations, BOM price omission, and cleanup. Final marker: `R3_ISOLATED_API_ACCEPTANCE_PASS`.
- PI-001: Replaced `4f6d8a2c1b90` with the complete reversible R3 schema; expanded ORM models and structured DTO/API handling for Product, Software, Algorithm, ModelCapability, Scene, Solution, relations, BOM, and price security; corrected seed product enums to `HARDWARE/SOFTWARE_PRODUCT/SYSTEM_PRODUCT/ACCESSORY`; populated normalized semantic child data; added Product/Software 1:1 `COMMERCIALIZATION`; removed invented metric values in favor of explicit pending-confirmation evidence. Python compileall and `git diff --check` pass.
- PI-000: Read the production implementation directive, current checkpoint, all R3 source-of-truth documents, the seven-sheet field dictionary, Git/runtime state, existing migrations, current API/UI, and frozen drafts. Decision: retain useful concepts but replace the unexecuted draft implementation with the complete R3 contract before migration or deployment.
- SDR3-001: Completed SIX CENTERS DESIGN REVIEW - R3 FINAL FREEZE at `six-centers-design-review-r3-20260822-182819/` and created verified ZIP `six-centers-design-review-r3-20260822-182819.zip`. Final content: 19 Mockups, six annotated detail views, nine design/proposal documents, seven-sheet field dictionary, review index, and portable local visual assets. All package, browser, semantic, no-price, raster-size, spreadsheet-container, and ZIP integrity gates passed. Formal runtime remained untouched.
- SDR2-001: Completed SIX CENTERS DESIGN REVIEW - REVISION ROUND 2 at `six-centers-design-review-r2-20260822-144038/`: 18 differentiated Mockups, six annotated detail views, eight design/proposal documents, updated review index, verified seven-sheet/157-row field dictionary, exact 1920x1080 raster QA, price-hidden assertions, browser console audit, and ZIP integrity verification. Formal runtime remained untouched.
- SDFR-001: Completed SIX CENTERS DESIGN FREEZE REVIEW package at `six-centers-design-review-20260822-125211/`: 18 mockups, six annotated mockups, eight required docs, exact UI-field mapping, relation/data/API proposals, implementation proposal, review index, and seven-sheet field dictionary. Visual and structural QA passed; formal runtime remained untouched.
- SDR-001: Completed `GENERATE_SIX_CENTERS_UI_AND_FIELD_DESIGN_FOR_REVIEW`; generated five design documents plus review index and recorded the frozen implementation draft without modifying the formal runtime.
- PH-001: Recorded the product-hardening KEEP/REFACTOR/MIGRATE/REMOVE decision from the deployed current-state baseline; no source, schema, runtime, or data mutation occurred.
- UI-ACCEPTANCE-EXPORT: Read the frozen V3 PRD and all nine embedded UI references; exported 46 live browser screenshots, UI/field/API/data-model/relation/seed/E2E reports, a verified 99-row field inventory workbook, and `ACCEPTANCE_INDEX.md`. Final decision remains `WAITING_FOR_EXTERNAL_UI_REVIEW`.
- V3-D13: Replaced the shipped frontend with `AppV3.vue`, removed the legacy monolith, closed responsive layouts at desktop/tablet/mobile breakpoints, localized statuses, and split production chunks.
- V3-D12: Added exact product price APIs, frozen price metadata, PRICE_VIEW omission for product and BOM payloads, same-page price maintenance, migration `a2c63a4f5798`, and removed independent price UI.
- V3-D11: Added idempotent semantic V3 seed upgrade and server audit for all minimum counts, 66+ meaningful relationships, per-solution BOMs, frozen fields, and zero dirty naming patterns.
- V3-D10: Completed generic bidirectional relationships, frozen metadata, searchable relation Drawer, add/remove APIs, cross-center navigation, and migration `f1b5293e4687`.
- V3-D9: Completed solution metadata, persistent standard BOM, PRICE_VIEW-safe BOM payloads, product-manager BOM editor, and migration `e0a4182d3576`.
- V3-D8: Completed scene-center frozen metadata, goals/process/capability content, localized CRUD/detail forms, and migration `d9f3071c2465`.
- V3-D7: Completed model-capability frozen metadata, metrics, input/deployment requirements, boundaries, localized CRUD/detail forms, and migration `c8e2f60b1354`.
- V3-D6: Completed algorithm-center frozen metadata, structured metrics and boundaries, localized CRUD/detail forms, and migration `b7d1e5fa0243`.
- V3-D5: Completed software-center frozen metadata, exact CRUD/detail rendering, product-manager form fields, and migration `a6c0d4e9f132`.
- V3-D4: Completed the frozen product create and detail workflow, type-aware dynamic fields, main-image field, embedded PRICE_VIEW-safe price response, and migration `f5b9c3d8e021`.
- V3-D3: Added exact APIs and a shared responsive detail framework for all six center routes, including real relationship links and permission-aware management/price sections.
- V3-D2: Connected all six centers to the shared enterprise list shell with card/list modes, filters, summary counts, responsive layouts, and complete loading/empty/error/permission states.
- V3-D1: Added the frozen three-permission model, role migration `e4f8a2c7d910`, six-center navigation, 模型能力中心 API alias, and all twelve Vue Router routes; frontend build and backend compile passed.
- V3-D0: Read the frozen V3.0 PRD in full, inspected all nine embedded UI references, created a clean baseline commit, and opened `feature/knowledge-centers-v3`; formal API 3.20 remained untouched.
- A01: Created independent formal project directory `/opt/haizhi-product-hub`; legacy `/opt/haizhi-product-center` and systemd service left unchanged.
- A02: Started isolated PostgreSQL container `haizhi-hub-postgres` on network `haizhi-hub-net` with named volume `haizhi_hub_pgdata`.
- A03: Built and deployed FastAPI service; health and seeded PostgreSQL product records verified.
- A04: Installed Docker Compose v2.32.4 at `/usr/local/lib/docker/cli-plugins/docker-compose`.
- A05: Published formal service on host ports 18080 and 443; port 80 legacy service remains unchanged.
- A06: Built frontend/backend update `haizhi-hub-api:1.2`; source package extracted at `/opt/haizhi-product-hub`.
- A07: Redis imported and verified `PONG`.
- A07b: Generated initial Alembic revision and verified a clean-database upgrade.
- A07c: Replaced production `create_all` startup with Alembic; rebuilt `haizhi-hub-api:1.5`, started it with `alembic upgrade head`, verified health, and verified the production revision.
- A07d: Added the migration revision, runtime URL override, pinned Alembic image layer, PYTHONPATH, and entrypoint to the local formal repository; `compileall` and static checks passed.
- A08a: Added MinIO client configuration, persistent object storage compose service, document upload/list endpoints with role enforcement and 50MB limit; local compile and `git diff --check` passed.
- A08b: Deployed `haizhi-hub-api:2.5`; health, admin login, MinIO health, upload/list, and direct object listing passed.
- A09a: Added normalized `Permission`/`RolePermission` models and authorization compatibility fallback.
- A09b: Added Alembic revision `f20c6e517c31` with portable role permission backfill; local and server compile checks passed.
- A09c: Production migration passed at `f20c6e517c31`, with 27 permissions and 74 assignments.
- A09d: Image 2.7 reproducible build passed with pinned `requirements.txt`; deployed and health/admin login passed.
- A10a: Product relationship and admin CRUD API code compiled locally and `git diff --check` passed.
- A10b: Image 2.8 built and deployed.
- A10c: Product capability read, admin CRUD success, sales CRUD denial, and delete-after-read 404 passed.
- A10d: Audit migration and admin create audit retrieval passed.
- B01a: Core business loop HTTP regression passed; GPU endpoint reachability passed, but application returned rule fallback because GPU response omitted `message.content`.
- B01b: AI extraction fixed; `/api/ai/requirement-analysis` returned `mode=llm` with non-empty GPU-generated content.
- C01a: Gateway and embedding endpoints implemented and synchronized; image 3.1 build started.
- C01b: Gateway governance and embedding tests passed on image 3.1.
- C01c: Dify source unpacked, ports/secrets configured, and required image set identified; Docker Hub pull timed out.
- C01d: RAG chunk model/API and corrected formal backup/restore scripts added and synchronized; image 3.2 build started.
- C01e: Corrected backup produced PostgreSQL and MinIO archives; disposable PostgreSQL restore passed with 16 products and 1 document chunk. DaoCloud mirror successfully began pulling Dify API image after Docker Hub timeout.
- C02a: Reconnected to formal server, verified API image 3.2 and rewrote enabled Dify Compose image references to DaoCloud.
- C02b: Pulled all enabled Dify 1.16.1 service images through DaoCloud.
- C02c: Started the 20-container/network Dify stack; all long-running core services are up and Dify API/PostgreSQL/Redis report healthy.
- B02a: Added API-backed document list and admin audit-log pages and verified the frontend production build.
- C03b: Added constant-time service-key authentication for Dify, retained JWT fallback, and exposed the governed model through `/v1/models` for OpenAI-compatible provider validation.
- C04a: Added training course persistence and Moodle launch metadata, `TRAINING_VIEW`/`TRAINING_ADMIN` APIs, audit logging, and the API-backed training page.
- C04b: Created a compact 1.06 MB server deployment source artifact `haizhi-product-hub-update-c04a.tgz` excluding local dependencies and build output.
- C04c: Transferred/extracted the C04a source artifact, created protected runtime gateway credentials, built frontend image `3.3` and backend image `3.4`, migrated production to `b460e9d728a2`, and deployed successfully.
- C03d: Initialized the Dify owner successfully; `/console/api/setup` returned success and setup state is `finished`.
- C03e: Connected `haizhi-hub-api` to `docker_default`; authenticated `/v1/models` and `/v1/chat/completions` from `docker-api-1` reached the governed GPU endpoint and returned normalized non-empty content.
- C03f-03: Official OpenAI API Compatible plugin package installed successfully in Dify as provider identifier `langgenius/openai_api_compatible:0.0.62@44a1acb04fb9cb34ed39ef6b82b2d6fa337cb32e87e364ff2ae64f24686552eb`.
- C03f-04: Dify credential validation returned success; the protected custom LLM credential was saved and the model list reports `/model/models/Qwen3.6-27B` as active.
- C03f-05: Created Dify app `f8b3872e-ee6a-4606-b33c-bf0e14ff16c6`, invoked it through `/console/api/apps/{id}/chat-messages`, received a non-empty governed response, and restored `FORCE_VERIFYING_SIGNATURE=true` without breaking subsequent invocation.
- C04d-01: Deployed persistent Moodle 5.0 and MariaDB 11.4 containers with protected runtime secrets, isolated network/volumes, and host port 18082; Moodle setup completed and Apache returned HTTP 303.
- C04d-02: Set the Moodle site identity, created representative course id 2, corrected persisted wwwroot and data-directory permissions, switched to database locks, and passed administrator authentication plus authenticated course view.
- C04d-03: Diagnosed the missing TrainingCourse class in the production image, synchronized the complete model source, built/deployed `haizhi-hub-api:3.5`, and passed training association create/list API checks.
- C04d-04: Deployed `haizhi-hub-gateway` on formal port 443, rebuilt clean frontend `3.5` and API `3.7`, verified no demo credentials in source/dist/browser, published Moodle at `/moodle/`, fixed the subpath redirect loop with a persistent Moodle code alias and prefix-preserving proxy, and passed authenticated browser course access.
- B03a: Added product-category API and complete browser CRUD controls, fixed 204-response handling, backfilled 15 representative product-capability relationships through migration `c81f0e2a91b7`, deployed API `3.10`, and passed API/browser CRUD plus RBAC acceptance.
- B03b: Added entity-specific permission enforcement and audited admin CRUD for software, algorithms, capabilities, scenes, and solutions; added permission-filtered navigation and browser CRUD controls.
- B03c: Added scene detail API/UI with business pain points and associated solutions; fixed the catalog serialization loop returning one record; deployed API `3.16` and passed live API/browser relationship acceptance.
- B04a: Made BOM recommendations condition-driven, validated requirement bounds, added saved-project detail/update/version/delete APIs, added project save/detail/delete browser workflows, deployed API `3.17`, and passed full API/browser cleanup acceptance.
- B05a: Added protected CSV price export and administrator price-access log API, enforced PRICE_VIEW/PRICE_EXPORT/COST_VIEW separation, deployed API `3.18`, and passed API/browser confidentiality acceptance.
- B06a: Added tender persistence and document associations, real upload/download/delete controls, permission-filtered tender workspace, oversized/empty/invalid-association rejection, MinIO outage recovery handling, deployed API `3.19`, migrated to `d92a6b7c31e4`, and passed API/browser cleanup acceptance.
- D01a: Removed deterministic bootstrap credentials from source, moved acceptance credentials to a protected server-only environment file, added login throttling and security headers, deployed API `3.20` as UID/GID 10001 with read-only rootfs, all capabilities dropped and no-new-privileges, removed nine stale credential-bearing static backups, and passed hardened full business regression.
- D02a: Created timestamped PostgreSQL and MinIO backups, verified non-empty artifacts and checksums, restored both into isolated disposable resources, validated schema/business counts/object inventory, removed disposable resources, and kept the formal API healthy.
- D03a: Rolled API `3.20` back to schema-compatible `3.19`, verified health, gateway, authenticated product access, Alembic `d92a6b7c31e4`, 16 products, and both Docker networks; restored hardened `3.20`, verified security headers/runtime/data, and removed obsolete stopped rollback containers.
- D04a-partial: Re-ran representative formal regression after rollback restoration: product, catalog, BOM/project, price, document/tender/training, embedding/RAG, governed model discovery, local LLM, Dify setup, Moodle gateway, and runtime checks passed; all created business records and files were cleaned up.

# TESTS PASSED
- PARAMETER-CRUD-FORMAL-20260907 PASS: formal product 38 parameter PATCH returned 200, a fresh GET showed the edited first value and one deleted row (count 2), restoration PATCH returned 200, and a fresh GET restored count 3. Port-80 gateway health passed and temporary test values were removed.
- MAIN-IMAGE-FORMAL-20260901 PASS: candidate `haizhi-hub-api:6.1.7-main-image-fix` served `index-D8fiEXLK.js` / `index-C0w9Bjj3.css`, contained `产品主图已保存并生效`, survived restart, and was promoted with rollback. Formal direct/gateway health and formal restart passed; Alembic stayed at `c3d4e5f60718 (head)`.
- MAIN-IMAGE-PRODUCTION-CHAIN-20260901 PASS: a real PNG uploaded to formal production, was immediately PATCH-bound to product 38, persisted in a fresh GET, returned HTTP 200, then the original image was restored and the temporary image was deleted and verified HTTP 404.
- MAIN-IMAGE-LOCAL-BUILD-20260901 PASS: product main-image upload now persists immediately, refreshes the same product's hero image by watching both record id and `mainImage`, and cleans up the uploaded object if product binding fails. `npm run build` emitted `index-FBF5DOfS.js` and `index-C0w9Bjj3.css`.
- MAIN-IMAGE-TRANSFER-20260901 PASS: `/tmp/main-image-fix.tgz` verified as 18,264 bytes with SHA-256 `937854eabb4239f7e69488d3af56b8ebc8322f79f8eaad44c71818959507f1d3`; `/tmp/frontend-src-complete.tgz` verified as 70,910 bytes with SHA-256 `13a23a6a6615290c792e11339ec45c2ed096afd9ce544c189980f8189a5b74c2`. Server rollback copies were created before source synchronization.
- UPLOAD-REAL-CHAIN-20260901 PASS: a real PNG uploaded as knowledge image id 14, returned HTTP 200 `image/png`, was bound to product 38, persisted through a fresh GET, then the original product image was restored and the test image was deleted (subsequent GET 404).
- DOCUMENT-REAL-CHAIN-20260901 PASS: test document id 44 uploaded and linked to product 38; a reader could not see the DRAFT, could see it after PATCH to PUBLISHED/CURRENT, preview returned 200, reader download returned 403, and cleanup returned subsequent preview 404.
- MATERIAL-FINAL-REGRESSION PASS: business root 200, Moodle 200, Dify setup 200, Alembic `c3d4e5f60718`, active counts 3/5/4/2/5, documents 26, preview failures 0, and knowledge images 7.
- MATERIAL-RESTART-STABILITY PASS: the `6.1.6-official-materials` candidate restart retained the official catalog, relations, tender parameters, images, and documents (`RESTART_STABILITY_PASS`).
- MATERIAL-API-SECURITY PASS: ordinary reader received no price keys; product 38 retained official scene/software relations and 12 tender parameters; reader preview 200, reader download 403, administrator download 200; image endpoint 200 `image/jpeg`.
- MATERIAL-EXTRACT PASS: official RAR returned `All OK`; extracted source count is exactly 25 files, with the generated manifest bringing the staging count to 26 before production inventory files were added.
- MATERIAL-DRY-RUN PASS: six production inventory CSVs and their SHA-256 values were written under `/opt/haizhi-product-hub/import/materials-20260826-103833`; no catalog/document mutation occurred.
- MATERIAL-BACKUP PASS: `/data/haizhi-product-hub/backups/20260826-102616-official-material-import/haizhi_hub.dump` and `minio-data.tgz` are non-empty; source workbook/RAR copies and all SHA-256 values are recorded in the same backup directory.
- UI-POLISH-D6 PASS: formal `haizhi-hub-api:6.1.0-ui-polish` is running with image id `sha256:45dffe7e0d2b4c23d01cf91a13eaa09928bd5d815d15952097818847cdac9bac`, identical to the accepted candidate; 18080 and 443 health returned HTTP 200; Alembic is `c3d4e5f60718 (head)`; frontend entry is `index-D4lSoA8j.js`.
- UI-POLISH-D4 PASS: required 01-17 screenshots plus four-view responsive evidence exist; AI Q&A, structured requirement analysis, recommendation, BOM Drawer/manual change/version/validation, Excel mapping/preview/generation, and document upload/preview interactions passed.
- UI-POLISH-D4 PASS: responsive scan at 1920x1080, 1600x900, 1440x900 and 1366x768 found no page-level horizontal overflow on home or BOM; 1366 document and Excel pages passed.
- UI-POLISH-D4 PASS: six-center list/detail browser regression is 12/12 with zero page errors, zero console errors and zero console warnings.
- UI-POLISH-D4 PASS: no-PRICE_VIEW/no-KNOWLEDGE_MANAGE account received no product price payload and HTTP 403 from price and knowledge-write endpoints.
- `PHASE2_FINAL_ZIP_VERIFY_PASS`: 80 ZIP entries; required Word report, Excel sample, and package manifest present; SHA-256 matched the companion checksum file.
- `PHASE2_REPORT_STRUCTURE_QA_PASS`: 9/9 required Markdown reports exist; Word report contains 71 paragraphs, 16 tables, 8 evidence figures, and 1 section.
- `PHASE2_WORD_RENDER_QA_PASS 19/19`: every final report page visually inspected at original resolution with no clipping, overlap, broken table, missing glyph, or footer/header defect.
- `PHASE2_DOCUMENT_SCREENSHOT_RECAPTURE_PASS`: formal `/documents` DOM and screenshot show the PRD document as 已发布 / 当前有效 / 已同步 with preview, original download, and edit actions.
- `PHASE2_TEMP_USER_15_DISABLED_PASS`: exact browser acceptance username verified and disabled after the audit-preserving database correctly rejected physical deletion.
- `PHASE2_STYLE_CANDIDATE_STOPPED_PASS`: temporary style candidate is exited; formal 6.0.5 and stopped 6.0.4 rollback remain preserved.
- PHASE2-IMPL-011J PASS: real in-app-browser responsive regression is 44/44 at 1920x1080, 1600x900, 1440x900 and 1366x768; homepage final widths are 1905/1905, 1585/1585, 1425/1425 and 1351/1351; six-center list/detail smoke is 12/12; console error/warn count is zero.
- PHASE2-IMPL-011J PASS: exact meaningless project id 5 (`嗯嗯嗯`) was inspected, deleted through the authenticated API, and verified absent; acceptance project id 6 remains at immutable BOM V3.
- PHASE2-IMPL-011I PASS: `PHASE2_LEGACY_PORT80_BACKUP_PASS`, `PHASE2_DIFY_PORT80_CANDIDATE_PASS`, and `PHASE2_DIFY_PORT80_FORMAL_PASS`; Dify setup reports `finished` through both port 80 and port 18081; 443 application health remains PASS.
- PHASE2-IMPL-011H PASS: project id 6 real BOM V3, authenticated final Excel download, rendered workbook inspection, document id 14 preview/original download, and `PUBLISHED/CURRENT/SYNCED` knowledge state passed.
- PHASE2-IMPL-004 PASS: `PHASE2_CANDIDATE_API_ACCEPTANCE_PASS`; real Product-backed BOM rows, manual-edit precedence, historical snapshot immutability, sales ERROR-override denial, administrator override audit, reader price/project denial, template formatting/content/hash, document governance and original-file download passed.
- PHASE2-IMPL-003 PASS: local Python compileall and `git diff --check`; candidate sales permission binding, migration reapplication, product-manager role-code correction, and UTF-8 Excel download regression passed as part of the complete candidate suite.
- PHASE2-IMPL-002 PASS: candidate migration `7a8c9d0e1f23 -> c3d4e5f60718 -> 7a8c9d0e1f23 -> c3d4e5f60718`; candidate health returned `runtime=fastapi-postgresql`.
- PHASE2-R2-DESIGN-006 PASS: ZIP expanded successfully with 9 R2 mockups, 6 annotated pages, 12 R2 documents and the R2 field dictionary; 7 updated, 2 new and 14 unchanged counts reconcile to the approved R1/R2 scope.
- PHASE2-R2-DESIGN-005 PASS: all 15 workbook sheets rendered and were visually reviewed; formula error scan matched zero entries and the R2 Document fields are populated.
- PHASE2-R2-DESIGN-004 PASS: all 15 R2 review PNGs are non-empty 1600x900 images; mockup source contains zero `AI产品顾问`, `多智能体中心` or `知识库中心` matches.
- PHASE2-DESIGN-006 PASS: matching ZIP expanded successfully; extracted package contains exactly 21 core mockup PNGs, 7 annotated PNGs, 14 required Markdown documents, the review index and the field dictionary workbook.
- PHASE2-DESIGN-005 PASS: all 14 workbook sheets rendered and were visually inspected; the BomEditor key range inspection returned populated values and the workbook scan matched zero formula errors.
- PHASE2-DESIGN-004 PASS: all 28 core/annotated screenshots are non-empty PNG files at exactly 1600x900; representative high-density pages passed visual review without obvious clipping, overlap or blank rendering.
- AD error hotfix passed frontend production build, backend compileall, diff check, checksum transfer, immutable image build, control-byte unit test, login-domain validation test, isolated JSON 502/persistence regression, formal health/static/API tests, stale RUNNING-run repair, and hardened runtime verification.
- AD 5.7.2 candidate and formal acceptance passed: frontend build, Python compileall, diff check, image build, migration upgrade/downgrade/re-upgrade, health, hardened runtime parity, manual configuration API validation, encrypted password persistence/no-response disclosure, blank-password preservation, connectivity failure handling, disabled-sync denial, Chinese roles, exact static assets, formal browser rendering, and temporary-account cleanup.
- AD-APPROVAL-006 formal: PostgreSQL backup SHA-256 `042266a46bc48a5db1ed2c1fdec291e3f8f8c4a47fe8ecd88a52f53a129ba24f`; MinIO backup SHA-256 `180aeaf8e6378defef8920e9381af25776f311aadded72eb6af7a8abfb9aac4a`; Alembic `2f7b6c8d9e10`; hardened image `haizhi-hub-api:5.7.1-ad-approval`; direct health PASS; `5.7.0` rollback retained.
- AD-APPROVAL-005 isolated: `AD_MANUAL_APPROVAL_ACCEPTANCE_PASS`; built-in roles all use Chinese names; English role names return 422; only checked candidates become login accounts; unchecked candidates remain absent; existing AD users update only after a later explicit confirmation; test records cleaned.
- MSA-008 formal: predeployment PostgreSQL/MinIO backups and SHA-256 PASS; health direct/gateway PASS; Alembic `9d3f4a6b8c21` PASS; exact `index-B2Oyoxph.js`/`index-PyoK1-X5.css` PASS; material import A/B identical and log-clean PASS; user/role CRUD PASS; USER_MANAGE denial PASS; PRICE_VIEW visible/removed/403 behavior PASS; temporary acceptance data cleanup PASS; source synchronization PASS; hardened UID 10001/read-only/cap-drop/no-new-privileges/two-network runtime PASS.
- MSA-007 isolated: clean migration to head, downgrade to `6a9c2e7d4f31`, re-upgrade PASS; importer twice returned products=3, variants=12, software=5, algorithms=4, scenes=5, capabilities=2 without warning/error; variants=12 and commercial profiles=9; complete system administration and price-security acceptance PASS.
- MSA-008 data quality: products=19, software=8, algorithms=14, capabilities=17, scenes=10, solutions=6, variants=12, commercial profiles=9, users=7, roles=7, permissions=30, dirty names=0.
- MSA-008 AD discovery: `10.1.1.102` ports 389 and 636 reachable; anonymous RootDSE returned `DC=hilaicloud,DC=com` and `adserver.hilaicloud.com`; deployed server/base/domain/default-role/filter metadata without a bind credential.
- IEA-005 formal: health PASS; Alembic `6a9c2e7d4f31` PASS; exact HTML/JS/CSS/Vue/Element chunks HTTP 200 PASS; six-center CRUD/RBAC/PRICE_VIEW/relation/BOM acceptance PASS; image upload/read/delete PASS; document upload/list/preview/download/delete PASS; ordinary-user download 403 PASS; manager download PASS; cleanup PASS; UID 10001/read-only/cap-drop/no-new-privileges/two-network runtime PASS; legacy port 80 HTTP 200 PASS; login page rendered with zero browser console warnings/errors.
- IEA-005 isolated candidate: migration/startup and health PASS; exact static chunks PASS; six-center acceptance PASS; image/document/RBAC acceptance PASS; all created test data and objects cleaned up.
- IEA-004 local final verification: `npm run build`, Python `compileall app migrations`, and `git diff --check` PASS. Final chunks: `index-BdlHTqbF.js`, `index-CFWYjkG5.css`, `element-C7nSBjN6.js`, `vue-DO8QNb4G.js`.
- UIF-006 formal smoke: health PASS; bundle `/assets/index-DsVeIerk.js` PASS; Alembic `4f6d8a2c1b90` PASS; counts Product 17, Software 3, Algorithm 10, Model Capability 15, Scene 5, Solution 6 PASS; six-center CRUD/RBAC/PRICE_VIEW/relation/BOM acceptance PASS; UID 10001 read-only runtime PASS; port 80 HTTP 200 unchanged PASS.
- UIF-005B isolated candidate: health PASS; final static bundle names PASS; read-only UID 10001 runtime PASS; six list/detail APIs PASS; product-manager CRUD PASS; ordinary-user write denial PASS; PRICE_VIEW omission PASS; bidirectional relation PASS with frozen `supportVersion` metadata; solution BOM PASS; cleanup PASS.
- PI-012 final local verification passed: `npm run build`, Python `compileall`, `git diff --check`, final ZIP integrity/checksum, and final report/artifact presence.
- PI-001 static verification passed: Python compileall for backend application and all Alembic migrations; `git diff --check`; no deprecated `AI_PRODUCT` or `SYSTEM_SOLUTION` remains in R3 seed logic; Product/Software commercialization seed mappings are explicit and relation-typed.
- PI-000 baseline audit passed: R3 package and required source-of-truth files are present; field dictionary contains the seven frozen center/relation sheets with zero formula-error matches; Git branch/commit and production application/database versions match the checkpoint; `4f6d8a2c1b90` is confirmed unexecuted because production head remains `a2c63a4f5798`.
- R3 final package structure passed: 49 files, 19 Mockups, six annotated detail views, required `FIELD_DICTIONARY.xlsx`, `FINAL_DESIGN_DECISIONS.md`, and `REVIEW_INDEX.md` all present and readable.
- R3 raster QA passed: all 19 Mockups and six annotated PNG files measure exactly 1920x1080.
- R3 browser QA passed on the clean export directory: all 18 standard screens load, no horizontal overflow is present, no serious console warnings/errors were recorded, all required local image assets returned successfully, and no `/artifacts/` image dependency remains in computed page visuals.
- R3 semantic Gates passed: Product image dominance/right-side business actions/recommendation layers; Software dashboard-only primary imagery; Algorithm input-process-output plus separated configuration parameters and measured metrics; Model test evidence with dataset/sample/resolution/hardware/runtime/date/source; Scene real bridge/ship/waterway visual; Solution structured architecture, capability coverage, and BOM.
- R3 PRICE_VIEW presentation assertions passed: product no-price mode contains no price tab/area; solution no-price mode contains no reference quote, unit price, subtotal, or total.
- R3 workbook QA remains passed: seven sheets, R3 ModelCapability metric-test fields and Solution capability-coverage fields present, zero formula-error matches, and readable rendered previews.
- R3 ZIP integrity passed: archive extracts successfully to the expected top-level directory with 49 files, 19 Mockups, six annotated views, 25/25 exact-size PNGs, readable Markdown documents, and a valid XLSX container containing `xl/workbook.xml`.
- Round 2 design differentiation passed: Product specifications, Software module matrix, Algorithm input-process-output pipeline, Model metric/contract view, Scene business matrix/flow, and Solution real-object architecture are distinct while sharing the same Design System.
- Round 2 product cards demonstrate radar, AI terminal, camera, and software-product-specific metrics; software assets use system UI imagery rather than hardware photos.
- Round 2 `price=0` assertions passed on product list, product detail, and solution detail: no price text, price panel, BOM unit-price header, subtotal header, or total appears.
- Round 2 browser console error count is zero; 18 Mockups and six annotated screenshots all measure exactly 1920x1080.
- Round 2 field dictionary contains 157 rows across Product 34, Software 21, Algorithm 20, ModelCapability 28, Scene 16, Solution 24, Relations 14; key range inspection, formula-error scan, and visual previews passed.
- UI acceptance export: 46/46 requested screenshot filenames exist and all measure exactly 1920×1080; representative workbench/product/software/algorithm/model/scene/solution and normal/admin images were visually inspected.
- UI field inventory: 99 rows across six centers exported to XLSX; key range inspection passed and formula-error scan returned zero matches; rendered preview was visually legible.
- Live price security: admin product detail included `price`, sales detail omitted the key; admin BOM included unit price/total, sales BOM omitted both.
- Non-destructive UI checks: product search returned one matching card; card/table switching, create/edit/price/relations dialogs, relation-remove confirmation cancel, and delete confirmation cancel passed without persistent mutation.
- Final live counts observed: products 16, software 3, algorithms 10, model capabilities 15, scenes 5, solutions 6, and six solutions with BOM. Product id 27 (`雷达`) appeared externally during the export and was preserved rather than modified.
- V3-D15-FINAL formal-state recheck passed after cleanup: API health ok on immutable `haizhi-hub-api:4.2`; Dify API, Moodle DB, and Moodle healthy; final semantic seed audit unchanged; no temporary report/checkpoint artifacts remain in application document data.
- V3-D15 report acceptance passed: 12-page DOCX generated; LibreOffice server render succeeded; every rendered page was inspected with no clipping, overlap, broken tables, missing glyphs, or footer/header defects; final a11y audit has 0 high-severity findings and 12/12 final raster pages match the inspected render pixel-for-pixel.
- V3-D14-14 browser console returned no entries; all six center list pages at the narrower 1280x720 live viewport reported `scrollWidth <= innerWidth` and no loading/error state. Responsive CSS breakpoints at 1450/1200/1050/1000/900/760/720/700/640/600 cover the required desktop matrices; six center screenshots are preserved under `artifacts/screenshots/`.
- V3-D14-13 final local verification passed: Python compileall, `git diff --check`, and frontend production build with 1,443 transformed modules.
- V3-D14-12 final data audit passed after browser CRUD cleanup: products=15, software=3, algorithms=10, model capabilities=15, scenes=5, solutions=6, solutions with BOM=6, relations=74, dirty records=0; migration remains `a2c63a4f5798`.
- V3-D14-11 Moodle false-negative health probe was diagnosed (`curl` absent in the image), corrected for both Moodle and MariaDB using image-native probes, and both containers returned healthy; `/moodle/login/index.php` returned 200 and course id 2 preserved the expected unauthenticated 303 redirect.
- V3-D14-10 Dify setup returned `finished`, Dify API health is healthy, and model discovery from the Dify network returned governed `/model/models/Qwen3.6-27B` with HTTP 200.
- V3-D14-09 embedding returned HTTP 200 with 32 dimensions, RAG returned HTTP 200 with a ranked result, governed gateway health returned 200/ok, and the local Qwen chat returned HTTP 200 with non-empty content.
- Formal gateway security headers passed: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, strict referrer policy, and restrictive CSP; API runtime remains UID/GID 10001, read-only rootfs, cap-drop ALL, no-new-privileges.
- V3-D14-08 administrator browser workflow passed: product card/list view, exact search, empty state, detail rendering, PRICE_VIEW section, relation Drawer, create at `/products/26?edit=1`, edit persistence, delete confirmation, and cleanup to the original 15-product count.
- V3-D14-07 ordinary-user browser acceptance passed for `/products`, `/software`, `/algorithms`, `/model-capabilities`, `/scenes`, and `/solutions`: seven expected navigation items including workbench, no create/edit/delete controls, no price text, no loading/error state; `/products/15` also omitted management and price sections.
- V3-D14-06 formal live six-center API acceptance passed: ordinary-user read-only access, administrator canonical CRUD, PRICE_VIEW omission, bidirectional relation create/delete, standard BOM update/read, and cleanup.
- V3-D14-05 V3 seed audit passed with 15 products, 3 software records, 10 algorithms, 15 model capabilities, 5 scenes, 6 solutions, 70 relations, and zero dirty records.
- V3-D14-04 formal deployment passed on `haizhi-hub-api:4.2`; health passed and production Alembic revision is `a2c63a4f5798`.
- V3-D14-03 pre-deployment PostgreSQL, MinIO, and source backups completed under `/opt/haizhi-product-hub/backups/`.
- V3-D13 frontend production build passed with 1,443 modules; application bundle reduced to 58.55 KB before gzip through vendor splitting; static audits found no legacy knowledge permissions, independent price page, model-management page, parameter-template page, negative letter spacing, viewport font scaling, or gradient use in shipped V3 source.
- V3-D12 frontend `pnpm build` passed with 1,443 modules transformed; backend/migration/security-test compile and `git diff --check` passed; executable security assertions are pending server runtime dependencies.
- V3-D11 backend/test compile, frontend `pnpm build` (1,443 modules), and `git diff --check` passed; the live `v3_seed_audit.py` is staged for execution immediately after migration/deployment.
- V3-D10 frontend `pnpm build` passed with 1,443 modules transformed; backend/migration compile and `git diff --check` passed; POST/DELETE relation routes and bidirectional serializers were source-verified.
- V3-D9 frontend `pnpm build` passed with 1,440 modules transformed; backend/migration compile and `git diff --check` passed; source checks verified BOM price fields are added only inside the PRICE_VIEW branch.
- V3-D8 frontend `pnpm build` passed with 1,440 modules transformed; backend/migration compile and `git diff --check` passed.
- V3-D7 frontend `pnpm build` passed with 1,440 modules transformed; backend/migration compile and `git diff --check` passed.
- V3-D6 frontend `pnpm build` passed with 1,440 modules transformed; backend/migration compile and `git diff --check` passed.
- V3-D5 frontend `pnpm build` passed with 1,440 modules transformed; backend/migration compile and `git diff --check` passed; source checks verified all frozen software fields in model, API, form, and detail UI.
- V3-D4 frontend `pnpm build` passed with 1,440 modules transformed; backend/migration compile and `git diff --check` passed; source checks verified the new product schema fields and conditional PRICE_VIEW response branch.
- V3-D3 frontend `pnpm build` passed with 1,437 modules transformed; backend `python -m compileall app migrations` and `git diff --check` passed; all exact non-product center list/detail route declarations were verified.
- V3-D2 frontend `pnpm build` passed with 1,434 modules transformed and production assets emitted.
- V3-D1 frontend `pnpm build` passed with 1,430 modules transformed; backend `python -m compileall app migrations` passed; `git diff --check` passed.
- `GET /api/health` returned `{"status":"ok","version":"1.0.0","runtime":"fastapi-postgresql"}` before the API recreation.
- PostgreSQL contained 15 seeded products.
- `sales` product access passed and price endpoint returned 403.
- BOM recommendation changed camera quantity from 4 to 6 when `ptz_count` changed.
- Redis password-protected health probe returned `PONG`.
- Frontend static root was served internally and externally through `http://10.1.2.1:443/` before v1.2 API recreation.
- Frontend production build passed after removing visible default credentials and adding project/price views.
- v1.2 frontend, authenticated identity, project list, and sales price denial checks passed through port 443.
- Fresh Alembic upgrade passed: revision `8c453412069a` and four representative business tables verified in a clean database.
- Production container startup migration passed: `haizhi-hub-api:1.5` starts successfully, `GET /api/health` succeeds, and production `alembic_version` is `8c453412069a`.
- Local formal migration startup files passed syntax compilation and contain no FastAPI lifespan `create_all` call.
- Storage round trip passed with PostgreSQL document id 1 and MinIO object `8939dad528e441eeb5460f7b318c8c09-hz-storage-test.txt`.
- Frontend production build passed after replacing document/admin placeholder views with real `/api/documents` and `/api/admin/audit-logs` data tables.
- Backend `compileall`, frontend production build, and `git diff --check` passed after adding Dify service authentication and `/v1/models` compatibility.
- Migration/module compile, frontend production build, and diff checks passed after adding Moodle course associations and the training page.
- Production health, Alembic revision `b460e9d728a2`, authenticated `/v1/models`, and new frontend asset serving passed on API image `3.4`.
- Dify setup state is `finished`; governed model discovery and chat from the Dify API container passed with non-empty normalized response content.
- Plugin installation task `01a022a2-e658-7af1-9e90-de2cc3d1d7e8` returned `success`, `1 success`, `installed`.
- Dify model credential validate returned HTTP 200 with `result=success`; credential creation returned HTTP 201 and model discovery returned `active`, `llm`.
- Dify chat application invocation returned HTTP 200 with `event=message`, `mode=chat`, and non-empty answer; HaiZhi gateway logs recorded the corresponding authenticated `POST /v1/chat/completions` HTTP 200.
- After restoring Dify plugin signature verification to `true` and recreating plugin-daemon, a second Dify application invocation returned HTTP 200 and non-empty content.
- Moodle MariaDB container is healthy; Moodle setup finished, Apache started, and local `GET http://127.0.0.1:18082/` returned HTTP 303.
- Moodle administrator authentication returned HTTP 200 and authenticated course id 2 returned HTTP 200 with the expected course title.
- HaiZhi `POST /api/admin/training/courses` returned 201 and authenticated `GET /api/training/courses` returned 200 with external course id 2 and its live Moodle launch URL.
- API image 3.7 returned health 200; gateway root returned 200; Dify container reached `haizhi-hub-api` health over `docker_default`.
- Browser login page had empty username/password fields and no visible demo credentials.
- Authenticated HaiZhi training page rendered the representative course and its launch URL pointed to `/moodle/course/view.php?id=2`.
- Moodle public course route redirected once to `/moodle/login/index.php`; administrator login completed and course id 2 rendered with the expected title.
- Live product acceptance passed: list, create, exact model search, detail relationship payload, update, sales read, sales price 403, delete, and post-delete 404.
- Browser product acceptance passed: list/search/detail, real core-capability rendering, admin create/edit/delete dialogs, success states, and empty search state after deletion.
- Production Alembic revision is `c81f0e2a91b7`; `product_capabilities` contains 15 representative relationships.
- Catalog acceptance passed for all five entity types: sales view, unauthenticated 401, unrelated-role 403, admin create/update/delete, solution-scene relation, scene-detail relation, and cleanup.
- Browser catalog acceptance passed for five real-data pages, admin create/edit/delete controls, empty-state support, and restricted-role navigation/home isolation.
- Browser scene detail displayed the bridge-collision pain points plus both standard and enhanced associated solutions.
- BOM/project acceptance passed base and changed rules, AIS exclusion, optional overheight/VHF inclusion, negative-input 422, sales edit 403, project create/list/detail/version update, sales update 403, delete, and post-delete 404.
- Browser generated a real BOM, saved it as a project, displayed the project/BOM detail dialog, deleted it, and rendered the empty project state.
- Price acceptance passed unauthenticated/sales denial, sales-support reference-only visibility, support export denial, price-admin/admin cost visibility, protected CSV export, and persistent VIEW/EXPORT audit verification.
- Browser confirmed sales support never receives a cost column or export command, while price admin receives both cost data and the export command.
- Document/tender live acceptance passed valid multipart upload with product/scene/tender relationships, sales list/download, unauthorized edit denial, empty/oversized/invalid-association rejection, tender CRUD, relationship detail, and cleanup.
- MinIO network outage returned 503 and recovery returned 200 after reconnecting the storage service.
- Browser acceptance passed permission-visible tender navigation, create/list/detail/delete, document upload controls, API-backed association display, download command, delete confirmation, empty states, and cleanup.
- Security acceptance passed source/served-asset secret scan, invalid and expired JWT rejection, five-failure login throttling with sixth request returning 429, CSP/nosniff/frame/referrer/permissions headers, API no-store caching, internal-only PostgreSQL/Redis/MinIO ports, non-root/read-only/capability-drop runtime, and all five live business suites on the hardened image.
- Backup artifacts passed: `backups/acceptance-d02/postgres-20260821-183306.sql` (87,505 bytes) and `backups/acceptance-d02/minio-20260821-183306.tgz` (7,686 bytes), with verified checksums.
- Disposable PostgreSQL restore passed at Alembic `d92a6b7c31e4` with products=16, users=7, documents=1, and chunks=1.
- Disposable MinIO restore passed with one object present; all disposable containers, volumes, and network were removed and the formal API remained healthy.
- Controlled rollback passed on API `3.19`: direct and gateway health, administrator login, product count 16, authenticated identity, Alembic `d92a6b7c31e4`, and `docker_default` plus `haizhi-hub-net` attachments all remained valid.
- Formal restoration passed on API `3.20`: UID/GID `10001:10001`, read-only rootfs, `cap-drop ALL`, `no-new-privileges`, hardened `/tmp`, both networks, security/no-store headers, gateway health, 16 products, and unchanged Alembic revision; obsolete stopped rollback containers were removed.
- Final product suite passed: list, admin create/search/detail/update/delete, sales read, price denial, and cleanup.
- Final catalog suite passed: all five entity views, unauthenticated/entity permission denials, admin CRUD, scene/solution relationships, and cleanup.
- Final BOM/project suite passed: conditional rules, invalid/unauthorized denial, project create/detail/version/update/delete, and cleanup.
- Final price suite passed: role confidentiality, protected CSV export, and persistent VIEW/EXPORT audit checks.
- Final representative document/tender/training flow passed with a real MinIO upload/download comparison, tender relationship, one published training course, and cleanup.
- Final Gate C checkpoint passed: two 32-dimensional embeddings, one RAG result, governed model `/model/models/Qwen3.6-27B`, local LLM mode with 2,075-character response, Dify setup `finished`, healthy Dify API, healthy Moodle database, and Moodle gateway HTTP 200.

# TESTS FAILED
- PRODUCT-PLATFORM-620 ISOLATED MIGRATION ATTEMPT 1 TRANSIENT: Alembic loaded application settings and refused to start because the migration-only container had no required `REDIS_URL` and `JWT_SECRET`. No migration ran and the isolated database remained at `c3d4e5f60718`. The retry will inject candidate-only required settings.
- MAIN-IMAGE-PRODUCTION-E2E-20260901 TRANSIENT/RESOLVED: JumpServer Web CLI temporarily stopped opening an SSH iframe during staging. Access later recovered; candidate/formal deployment, restart stability and real production upload/bind/restore/cleanup then passed.
- UPLOAD-CONTENT-VALIDATION-20260901 FAIL: arbitrary text bytes named `not-image.jpg` and sent as multipart `image/jpeg` were accepted as knowledge image id 15. The test record/object was deleted immediately. Backend currently trusts the client MIME header and does not decode or verify image content.
- INLINE-DOCUMENT-PUBLISH-20260901 FAIL: `DocumentAssets.vue` uploads directly as `DRAFT` and offers preview/download/delete only; it has no metadata/status/publish action. Ordinary users therefore cannot see newly uploaded files even though the manager receives a generic “资料上传成功” message.
- IMAGE-EDIT-PERSISTENCE-20260901 FAIL: `ImageUpload.vue` creates the storage/database object immediately but only updates an in-memory draft. Product and center records are not linked until the user separately clicks “保存全部修改”; cancel/navigation leaves an orphan upload and the UI does not warn that the image is not yet applied.
- CREATE-IMAGE-ENTRY-20260901 FAIL: non-product create dialog still renders a raw `cover_image` URL input rather than an upload control, so create and edit workflows are inconsistent.
- Final cleanup physical DELETE of temporary user id 15 returned HTTP 500 because historical audit rows retain a required user foreign key. The exact account was subsequently disabled through the authenticated administration API and verified unable to remain enabled; audit history was preserved.
- Initial style-fix candidate bind to localhost port 18090 failed because the port was already occupied. The failed container was removed, candidate port 18086 was used, and all candidate/formal checks passed.
- Initial six-center detail smoke used aggregate counts as record IDs and correctly returned not-found states. The actual first persisted IDs were queried and all 12 list/detail checks then passed.
- PHASE2 candidate acceptance attempts before the final pass exposed and fixed: sales missing `BOM_EDIT`; non-canonical bridge-scene fixture selection; misuse of a sales-support account as an ordinary reader; contaminated isolated rules after interrupted runs; and an HTTP 500 from an unencoded Chinese Excel download filename. Each failure was diagnosed, fixed, the isolated database was restored from the verified snapshot, and the full suite was rerun to PASS.
- Live AD authentication returned Active Directory subcode `52e`, meaning the supplied bind username/password was rejected. The screenshot also showed Login Domain incorrectly set to a Base DN; it must be `hilaicloud.com`. Candidate enumeration remains pending corrected credentials.
- V3-D12 local execution of `tests/v3_price_security.py` could not start because both available Windows Python runtimes lack the installed SQLAlchemy dependency; the test itself compiles and must run inside the API image after deployment.
- External `http://10.1.2.1:18080/` is blocked by firewall; port 443 is used as the temporary formal entry.
- HTTP `HEAD /` returns 405 because the static catch-all supports GET; GET root passed.
- Final Dify console re-login probe returned HTTP 401 `Invalid encrypted data` because Dify 1.16.1 requires client-side public-key encryption for the password field. This did not invalidate the previously passed Dify provider/application invocation or current healthy Dify runtime; no credential or runtime changes were made during the pause checkpoint.
- V3-D14 integration runner attempt 1 failed because the immutable API image does not include `requests`; attempt 2 failed due the response key typo `accessToken`; the runner was corrected to installed `httpx` and `access_token`, then the complete integration regression passed.
- Moodle briefly became unavailable while correcting its health check because an overly broad replacement also changed the MariaDB probe. The MariaDB-native probe was restored, both containers were recreated against persistent volumes, and database/Moodle health plus gateway HTTP checks passed with course data preserved.

# CURRENT ERRORS
- No current candidate migration error. The missing-setting failure was resolved by injecting migration-only `REDIS_URL` and `JWT_SECRET`; production was never touched.
- Candidate acceptance runner attempt 1: target host has no `python3` command. Use the API image's bundled Python or a preinstalled host interpreter; this is an execution-environment issue only and does not affect candidate API health.
- Candidate acceptance runner attempt 2: API container is correctly read-only, so `docker cp` cannot place a test file inside it. Use a disposable test-runner container sharing the network instead; do not weaken the candidate container.
- Candidate acceptance runner attempt 3: image entrypoint ran Alembic before the test script, producing missing-settings errors. Retry with `--entrypoint python`; no candidate or production data changed.
- No current deployment/runtime error for the main-image fix. A signed-in visual browser interaction remains to confirm the live edit-mode hero-image transition and reload persistence end to end.
- Upload and asset UI is not ready for business acceptance: draft publication is missing from inline document management, image-link persistence is ambiguous, create dialogs lack consistent upload controls, and server-side image content validation is insufficient.
- No application-blocking code, migration, import, runtime, or API errors remain.
- The earlier guessed PostgreSQL role `haizhi` was incorrect; production inspection established the correct role/database as `haizhi_app` / `haizhi_hub`, and the backup now passes. This is resolved and must not be treated as a current blocker.
- Physical DELETE of an account that owns retained audit rows returns HTTP 500 because the audit foreign key is intentionally non-nullable. The temporary acceptance account is disabled and verified; operational cleanup must preserve audit history through disable rather than physical deletion.
- AD/LDAP was explicitly excluded from reconfiguration and credential diagnosis in this UI-only phase; existing LDAP code was not modified and is not a Phase 2 UI acceptance blocker.
- Public port 443 now serves Dify over plain HTTP; a domain and trusted certificate have not been supplied.
- No unresolved material-import errors remain. Official catalog cleanup and import completed through reversible archival; no unrelated production record was physically deleted.

# FIXES APPLIED
- Changed product main-image upload from draft-only behavior to immediate product binding, record reload and visible hero-image refresh; added failure cleanup and same-id `mainImage` watcher coverage.
- Corrected Dify's stale Celery broker password to the URL-encoded active Redis password, refreshed the affected services and Nginx upstream resolution, and added governed real-dataset retrieval plus deterministic document-content fallback to AI Q&A.
- Sanitized LDAP/AD control bytes before database persistence or HTTP response, preventing PostgreSQL `NUL` failures and preserving structured JSON errors; added frontend non-JSON fallback and rejected Base-DN-shaped Login Domain values.
- Replaced environment-only AD configuration with administrator-managed LDAP/LDAPS settings, explicit enable/test/save/sync actions, encrypted password-at-rest handling, and blank-password update preservation; secrets are never returned by the API.
- Changed AD synchronization from direct account mutation to pending candidate batches plus selected-only confirmation, so administrators explicitly control who may log in.
- Added Chinese-only role-name validation and localized all built-in role and permission display names; frontend role codes and permission codes are no longer exposed.
- Fixed `permit()` indentation that caused a runtime `NameError` during dependency construction.
- Replaced destructive variant-list replacement with model-code upsert so the official material importer is idempotent and preserves manually maintained variants.
- Added `back_populates` to Product/ProductVariant and assigned USER_MANAGE during clean-database bootstrap.
- Added reachable AD RootDSE metadata while keeping bind credentials out of code, artifacts, images, and browser-visible configuration.
- Corrected the PostgreSQL permission-freeze migration ambiguity and canonical six-center CRUD/deletion cleanup paths; deployed immutable API `4.2`.
- Replaced the broken Moodle `curl` health check with the image-native PHP probe and restored the MariaDB health check with `mariadb-admin`; both persistent services are healthy.
- Removed visible and prefilled test credentials from login UI.
- Replaced project and price placeholder views with API-backed tables.
- Imported Redis under its mirror tag and created the local `redis:7.4-alpine` tag.
- Increased Dify plugin Python environment initialization timeout from 120 to 900 seconds after the first dependency installation was killed for inactivity; disabled mandatory signature verification only for the locally packaged official-source plugin.
- Replaced the stale frontend artifact with a no-cache production build, deployed API image 3.7, and removed browser-visible/prefilled credentials.
- Fixed Moodle's `/moodle/` reverse-proxy loop by preserving the path upstream, adding a persistent Moodle subpath alias, and removing the incorrect `proxy_redirect` rewrite.
- Fixed product deletion UI by accepting successful 204 responses without attempting JSON parsing.
- Replaced the disabled product button and placeholder capability panel with real admin CRUD interactions and API-backed relationships.
- Fixed catalog view permission leakage, restricted-role stale-page retention, unauthorized home shortcuts, and one-record-only catalog serialization.
- Fixed static BOM recommendations so feature toggles and camera quantities alter output, added invalid-input validation, and completed persistent project version lifecycle.
- Added no-store UTF-8 CSV export and explicit price access audit reporting; restricted cost rendering and export commands to the correct permission sets.

# SERVICES
- Legacy Python 2.7/SQLite `haizhi-product-center` is stopped and disabled after a complete verified backup; its code and data were not deleted.
- Formal: FastAPI/Vue/PostgreSQL/Redis/MinIO through the public business gateway on port 80; Dify 1.16.1 on public port 443 and retained direct port 18081; Moodle on port 18082 and business-gateway route `/moodle/`.

# CONTAINERS
- `haizhi-hub-api`: running formal `haizhi-hub-api:6.1.7-main-image-fix` on host port 18080; direct/gateway health, restart stability, static marker and live image upload/bind/restore/cleanup regression pass.
- `haizhi-hub-api-v616-main-image-rollback-20260901-175004`: stopped immediate rollback point on immutable `haizhi-hub-api:6.1.6-official-materials`.
- `haizhi-phase2-style-candidate`: stopped after final style verification; retained only as a non-running diagnostic artifact.
- `haizhi-phase2-pg`: running isolated candidate PostgreSQL restored from the verified production snapshot; no production database writes.
- `haizhi-phase2-api`: running candidate `haizhi-hub-api:6.0.0-phase2-runtime` at `127.0.0.1:18089`; health and complete Phase 2 candidate API acceptance pass.
- `haizhi-hub-postgres`: running.
- `haizhi-hub-redis`: running, password protected.
- `haizhi-hub-minio`: running with persistent named volume.
- `haizhi-hub-api-v605-uirollback-20260825`: stopped immediate rollback point on immutable `haizhi-hub-api:6.0.5-phase2-style-fix`.
- `haizhi-hub-api-v604-stylerollback-20260824`: stopped immediate rollback point on immutable `haizhi-hub-api:6.0.4-phase2-download-fix`.
- `haizhi-dify-port443`: running as UID/GID `101:101` with read-only root, capability drop `ALL`, `no-new-privileges`, hardened `/tmp`, and restart policy `unless-stopped`; proxies public port 443 to the existing Dify Nginx service.
- `haizhi-dify-port80-retired-20260825-223319`: stopped rollback copy of the former public-port-80 Dify proxy.
- `haizhi-hub-api-v572-adconfig-rollback-20260823`: stopped immediate rollback point on immutable `haizhi-hub-api:5.7.2-ad-config-ui`.
- `haizhi-hub-api-v571-adrollback-20260823`: stopped immediate rollback point on immutable `haizhi-hub-api:5.7.1-ad-approval`.
- `haizhi-hub-api-v570-adrollback-20260823`: stopped immediate rollback point on immutable `haizhi-hub-api:5.7.0-material-admin`.
- `haizhi-571-candidate` and `haizhi-571-pg`: isolated acceptance resources; candidate health, migration downgrade/re-upgrade, and manual approval workflow passed.
- `haizhi-hub-api-v563-material-rollback-20260823`: stopped immutable rollback point on `haizhi-hub-api:5.6.3-inline-edit`.
- `haizhi-570-candidate` and `haizhi-570-pg`: stopped after isolated migration/import/RBAC acceptance; retained temporarily as diagnostic evidence.
- `haizhi-hub-api-v562-inline-rollback-20260823`: stopped retained rollback point on immutable `haizhi-hub-api:5.6.2-inline-edit`.
- `haizhi-inline-candidate-563`, `haizhi-inline-candidate`, and `haizhi-inline-pg`: stopped after isolated acceptance; retained temporarily as non-running diagnostic records.
- `haizhi-hub-gateway`: running on host port 80; connected to `haizhi-hub-net` and `haizhi-moodle-net`.
- `haizhi-moodle-db`: running and healthy with persistent named volume.
- `haizhi-moodle`: running after completed Moodle setup, mapped to host port 18082 with persistent application/data volumes.
- `haizhi-hub-api-v41-20260822-022807`: stopped retained rollback point on immutable `haizhi-hub-api:4.1`; candidate, 4.0, and pre-V3 stopped containers were removed.

# PORTS
- 80: formal Nginx gateway serving HaiZhi at `/` and Moodle at `/moodle/`.
- 443: formal Dify 1.16.1 login/console entry; plain HTTP pending domain/certificate.
- 18080: formal FastAPI/static frontend internal/new-service port.
- 18081: retained direct Dify entry.
- 18082: Moodle training service.
- PostgreSQL and Redis are internal Docker network only.

# DATABASE VERSION
- PostgreSQL 16 Alpine container. Production schema is at Alembic revision `c3d4e5f60718`.
- Isolated candidate schema is at Alembic revision `c3d4e5f60718`; upgrade/downgrade/re-upgrade passed after the Phase 2 role-binding change.

# APPLICATION VERSION
- Formal backend/frontend deployed: immutable `haizhi-hub-api:6.1.8-parameter-persistence`; frontend entry remains `index-D8fiEXLK.js`, stylesheet `index-C0w9Bjj3.css`.
- Source branch/commit for the official-material changes: `codex/phase2-ui-final-polish` at `dde4761140b75b27bb722e606e3729cfbab55e55`; the working tree contains the recorded official-material source and artifact changes and has not been discarded.
- Candidate runtime: `haizhi-hub-api:6.0.0-phase2-excel-ui` on localhost port 18089; exact candidate frontend entry is `index-Da_32jig.js` and includes real Dify synchronization/retrieval, derived document previews, and visual Excel mapping/export.
- Server project root `/opt/haizhi-product-hub` is not a Git worktree, so it has no branch or commit identifier; deployment is artifact/image based.
- Local project is a Git worktree on `codex/phase2-ui-final-polish`.

# GIT STATE
- Server formal root: `NOT_A_GIT_WORKTREE`; branch and commit are not applicable.
- Local project branch: `codex/phase2-ui-final-polish`.
- Phase 2 UI productization implementation commit: `9fbf92c` (`feat: productize phase 2 user workflows`).
- Phase 2 implementation commit: `1c91a3a70ff8e48da710875e2f7c517634e89d2a` (`feat: deliver phase 2 business workflows`).
- LDAP error sanitization, frontend response fallback, login-domain validation, and 5.7.3 deployment checkpoint commit: `fbbe6eb` (`fix: sanitize LDAP errors and validate login domain`).
- AD manual configuration implementation and deployment checkpoint commit: `c125f4c` (`feat: add manual AD directory configuration`).
- Material/system-administration implementation commit: `41c6adf` (`feat: import official materials and add system administration`).
- Local implementation commit: `1f1e0aa68aeafcf307a6234ede90cc7757165516` (`feat: add inline knowledge editing and asset permissions`).
- Local implementation acceptance commit: `afba5a0b7ef718a58d7c276b0bfb00bd5188932b`.
- Local acceptance report commit: `3c3bee2e5135665b7add2c13d57b6215d057256b`.

# UNCOMMITTED CODE
- Phase 2 implementation is committed at `1c91a3a`; only final reports/evidence/checkpoint/package metadata are pending the final delivery commit. `frontend/tsconfig.tsbuildinfo` remains intentionally excluded generated metadata; unrelated existing artifacts remain untouched.
- LDAP error hotfix source, frontend build assets, deployment state, and regression results are committed at `fbbe6eb`; no related application source remains uncommitted.
- AD manual configuration implementation, migration, UI, deployed frontend assets, and deployment checkpoint are committed at `c125f4c`; no related application source remains uncommitted.
- Material import, variant/commercial models, system administration, AD integration, migration `9d3f4a6b8c21`, and the runtime acceptance script are committed at `41c6adf`; only checkpoint updates and generated `frontend/tsconfig.tsbuildinfo` remain uncommitted among files touched by this phase.
- Inline editing, image/document management, download permission, migration, and acceptance test implementation is committed at `1f1e0aa68aeafcf307a6234ede90cc7757165516`.
- Untracked design-review exports, render intermediates, extraction/build intermediates, and audit-only files remain intentionally excluded. They are user-owned or reproducible evidence and do not affect the deployed application.
- `frontend/tsconfig.tsbuildinfo` remains intentionally uncommitted as generated build metadata.
- Formal server deployment is artifact/image-managed at `/opt/haizhi-product-hub`; V3 source and immutable images are deployed.

# DIFY STATUS
- PASS: Dify 1.16.1 core services are healthy on public port 443 and retained direct port 18081; setup is finished; the administrator password was reset through the official Flask CLI and the new credentials returned HTTP 200 with authentication cookies; official OpenAI API Compatible plugin 0.0.62 is installed; protected HaiZhi Qwen3.6-27B model is active; signature verification is `true`; real document synchronization and retrieval pass against dataset `6b164760-8c9b-4c37-b0f7-96864d88b9c3`.

# MOODLE STATUS
- PASS: persistent Moodle 5.0/MariaDB 11.4 stack, administrator login, representative course id 2, HaiZhi training association APIs, formal `/moodle/` publication, browser login, and authenticated course rendering pass.

# LLM STATUS
- PASS: Local OpenAI-compatible endpoint `http://10.1.2.4:6999`, model `/model/models/Qwen3.6-27B`; authenticated HaiZhi Gateway discovery/chat, normalization, Dify provider validation, and Dify application invocation all pass.

# EMBEDDING STATUS
- Deterministic 32-dimensional embedding, chunk persistence, and semantic retrieval endpoints deployed and verified.

# EXTERNAL BLOCKERS
- ACTIVE 2026-09-20: JumpServer authenticated SFTP and Web CLI pages render, but their Upload/CONNECT controls do not respond to automated semantic, coordinate, or keyboard activation. The exact fix4 archive is not present in the server staging directory, so candidate build/deployment cannot safely proceed until the archive is transferred or the JumpServer controls recover. Required local artifact: `artifacts/haizhi-product-platform-6.2.0-source-fix4.tar.gz`, 8,763,475 bytes, SHA-256 `82c94432306d625d9db614e6cb33338650b5df761066dda3cefe764f57c91fe1`.
- RESOLVED 2026-09-01: JumpServer Web CLI access was restored and the staged fix was built, accepted, promoted and restart-tested. No current server-access blocker remains.
- None for Phase 2 UI & Interaction acceptance. Production trusted HTTPS remains a known infrastructure limitation because no domain/certificate has been provided; current entry is plain HTTP on port 443.
- None for the requested material import. The workbook and RAR are available on the server and the required rollback backup is complete.

# DO NOT REPEAT
- Do not repeat the official-material import, active-record archival, image upload, document upload, tender-parameter import, or final regression unless the user supplies changed source materials or explicitly requests a re-import. Current production marker is `haizhi-hub-api:6.1.6-official-materials` and final regression passed on 2026-08-26.
- Do not repeat server-side extraction or production inventory export unless the source RAR or production catalog changes. Current staging: `/opt/haizhi-product-hub/import/materials-20260826-103833`.
- Do not repeat the material-import preflight database/MinIO/source backup unless production data changes before import. Verified backup: `/data/haizhi-product-hub/backups/20260826-102616-official-material-import`.
- Do not regenerate or recompress the final package unless a delivered report/evidence file changes. Verified ZIP SHA-256 is `b63603cb04854d2bb4b1d8a0da0b576e2f2e5328c433798b5fa61b2df6b41291`.
- Do not repeat the 44-route responsive regression, 12-route six-center smoke, or scoped-CSS diagnosis unless frontend assets change; formal marker is `PHASE2_STYLE_FIX_FORMAL_GATEWAY_PASS`.
- Do not repeat the legacy port-80 backup or Dify sidecar cutover unless port routing changes; backup is `/data/haizhi-product-hub/backups/20260824-phase2-port80-cutover` and marker is `PHASE2_DIFY_PORT80_FORMAL_PASS`.
- Do not repeat the Excel visual-mapping candidate acceptance unless template analysis, mapping, workbook rendering, or export persistence changes; marker is `EXCEL_VISUAL_MAPPING_CANDIDATE_ACCEPTANCE_PASS`.
- Do not repeat the Phase 2 document-preview dependency build or DOCX/PPTX/XLSX upload-preview-download cleanup acceptance unless preview code or runtime dependencies change.
- Do not repeat the Phase 2 base candidate image creation, production snapshot checksum verification, or `c3d4e5f60718` migration rollback cycle unless runtime/schema source changes invalidate them.
- Do not repeat the pre-fix candidate failures. The clean final candidate marker is `PHASE2_CANDIDATE_API_ACCEPTANCE_PASS`; rerun the full suite only after subsequent Phase 2 integration changes.
- Do not repeat the 5.7.3 NUL-error diagnosis, isolated regression, formal deployment, or hardened runtime verification unless LDAP error handling/UI code changes.
- Do not repeat the 5.7.2 build, isolated migration rollback cycle, `AD_CONFIG_API_ACCEPTANCE_PASS`, formal backup, deployment, static/API/browser acceptance, or temporary-account cleanup unless AD configuration code/schema/runtime changes.
- Do not prefill, hardcode, or move LDAP host/Base DN/bind credentials back into backend environment defaults; configuration is intentionally administrator-managed in the UI.
- Do not repeat the 5.7.1 isolated migration downgrade/re-upgrade or `AD_MANUAL_APPROVAL_ACCEPTANCE_PASS` suite unless AD approval code/schema changes.
- Do not repeat the 5.7.1 formal PostgreSQL/MinIO predeployment backups or deployment unless source/runtime/schema changes; both checksums and the stopped 5.7.0 rollback container are recorded.
- Do not repeat the 5.7.0 clean migration/import/API/RBAC/PRICE_VIEW acceptance unless application or schema code changes; isolated and formal runs passed.
- Do not repeat official material import to prove idempotency; two isolated and two formal consecutive imports passed. Future runs are allowed only when official source material changes.
- Do not delete the stopped `haizhi-hub-api-v563-material-rollback-20260823` until business acceptance of 5.7.0.
- While `NEXT EXACT STEP` is `WAITING_FOR_EXTERNAL_FINAL_DESIGN_REVIEW`, do not modify formal Vue/FastAPI code, models, migrations, database, formal CSS/tokens, Seed Data, deployment, services, or runtime pages. Do not start implementation until the user explicitly provides `DESIGN APPROVED`.
- While `NEXT EXACT STEP` is `WAITING_FOR_EXTERNAL_DESIGN_REVIEW_R2`, do not code, execute/build migrations, deploy, mutate formal data, change running pages, or continue six-center implementation. Resume only after explicit `DESIGN APPROVED` or specific Round 2 design feedback.
- While `NEXT EXACT STEP` is `WAITING_FOR_EXTERNAL_DESIGN_CORRECTION`, do not code, execute/build migrations, deploy, mutate formal data, or alter the running UI. Only design corrections are allowed until an explicit `DESIGN APPROVED` decision.
- While `NEXT EXACT STEP` is `WAITING_FOR_SIX_CENTERS_DESIGN_REVIEW_DECISION`, do not modify business code, execute/build the draft migration, build or deploy the application, mutate formal data, or change the running UI.
- Do not repeat the UI acceptance export; use the existing timestamped export as the review baseline.
- Do not edit/delete product id 27 (`雷达`) without explicit external product-review instruction; it appeared during the audit and was not created by the audit process.
- Do not modify/delete/replace legacy port 80 service.
- Do not re-download Docker Compose v2.32.4; installed and verified.
- Do not re-import Redis image unless removed; image and container verified.
- Do not repeat v1.2 frontend build unless source changes.
- Do not download packages to the user's computer. All future downloads must occur on `172.20.1.7`.
- Do not repeat the Dify image pull unless an image is explicitly missing; all enabled service images were pulled and the stack started successfully.
- Do not recreate Moodle volumes or repeat initial Moodle installation; persistent setup completed successfully.
- Do not repeat B06a oversized upload or MinIO outage tests unless document/storage code changes; both passed and storage recovered.
- Do not repeat D01a full hardened business regression or destructive login-rate sequence unless authentication/runtime code changes; both passed and the API was restarted cleanly.
- Do not repeat D02a full backup/restore unless storage or schema changes; PostgreSQL and MinIO backup, checksum, isolated restore, validation, and cleanup passed.
- Do not repeat D03a controlled rollback unless application image/runtime/schema changes; rollback to `3.19` and restoration to hardened `3.20` passed with data preserved.
- While `NEXT EXACT STEP` is `WAITING_FOR_EXTERNAL_REVIEW_AND_OPTIMIZATION_INSTRUCTION`, do not add features/pages/fields/seed data, change UI, mutate formal data/runtime, or stop services without new review feedback.
- Do not repeat V3 deployment, full live API acceptance, browser CRUD, integration regression, report render, or backup work unless subsequent source/runtime changes invalidate those results.

# GATE A
PASS FOR PRODUCT/UI REVIEW: frontend/backend/PostgreSQL/Redis/MinIO/Docker/Alembic, formal reverse proxy, health, hardened runtime, security headers, and final runtime regression pass. Trusted TLS remains an external production-launch dependency.

# GATE B
PASS: product, catalog, scenario/solution, BOM/project, price, documents, and tender-support business loops pass through API and browser acceptance.

# GATE C
PASS: Dify application, AI Gateway/LLM governance, deterministic Embedding/RAG, and Moodle deployment/integration/browser launch pass.

# GATE D
PASS: RBAC, price audit, source/asset secret scan, authentication controls, security headers, network isolation, least-privilege API runtime, backup/restore, and controlled upgrade/rollback acceptance pass.

# FINAL UI GATES
- FUNCTIONAL GATE: PASS.
- UI GATE: PASS.
- INTERACTION GATE: PASS.
- PERMISSION GATE: PASS.
- RESPONSIVE GATE: PASS.
- REGRESSION GATE: PASS.
- FINAL STATUS: `PHASE 2 UI & INTERACTION ACCEPTED`.

## 2026-09-21 图片展示修复跟进

- 用户反馈正式线上产品卡片主图仍被裁切；仅针对该问题处理，未操作 Dify、端口或数据库数据。
- 通过 JumpServer Web CLI 在正式 API 容器上完成可回滚切换：`haizhi-hub-api:6.2.0-imagefix4`。
- 发布目录：`/opt/haizhi-product-hub/releases/6.2.0-20260921-fix5-full`。
- 修复内容：产品卡片图片区域高度由 154px 调整为 210px；图片元素改为绝对定位铺满容器，并强制 `object-fit: contain`、`object-position: center`，避免图片固有高度撑大后被父容器裁切。
- 正式旧容器回滚点保留：`haizhi-hub-api-imagefix3-rollback-20260921`。
- 已验证：`/api/health` 返回 `status=ok`；容器 `ReadonlyRootfs=true`、用户 `10001:10001`；正式数据库未清空、未重新导入。
- 已使用 `admin / admin2026!` 登录正式业务平台并实测 `/products`：主图完整显示，浏览器 DOM 中 `object-fit=contain` 且图片不再超出 210px 容器；截图验证通过。

## 2026-09-21 品牌与背景 UI 修改

- 本地已完成品牌文案改为“海莱云智产品中心”，移除登录页“六大知识中心”标题。
- 登录后导航维持并明确为：首页、智能配单、项目配单、资料中心、产品中心、软件中心、算法中心、模型能力中心、场景中心、方案中心、BOM规则、Excel模板、系统管理。
- 已使用用户提供的海港图片作为登录页及内容区域背景，并完成本地 `npm run build`。
- 本地发布包：[haizhi-ui-brand-bg-20260921.tar.gz](C:/Users/kn319/Documents/New%20project/haizhi-product-hub/haizhi-ui-brand-bg-20260921.tar.gz)，SHA-256 `FB1FC60ABEFBA4CF52ED2924359D3B6CEDC4F5ED84DC7CC501439F878235AA3F`。
- 通过堡垒机文件管理已上传发布包和压缩背景图；正式服务切换尚未执行，需在服务器终端重新连接后部署并保留回滚容器。
## 2026-09-21 品牌与背景正式上线

- 正式镜像：`haizhi-hub-api:6.2.0-brand-bg2`
- 回滚容器：`haizhi-hub-api-imagefix4-rollback-brand2-20260921`
- 发布包：`haizhi-ui-brand-bg-20260921.tar.gz`
- 发布包 SHA-256：`fb1fc60abefba4cf52ed2924359d3b6cedc4f5ed84dc7cc501439f878235aa3f`
- 背景图：`hilai-harbor-bg.jpg`
- 健康检查：`/api/health` 返回 `{"status":"ok","version":"1.0.0","runtime":"fastapi-postgresql"}`
- 安全参数复核：非 root `10001:10001`、只读根目录、`CapDrop=ALL`、`no-new-privileges`、`unless-stopped`
- 正式数据未迁移、未清空、未覆盖；产品列表刷新后仍为 4 条
- 浏览器验证：品牌显示“海莱云智产品中心”，导航顺序符合要求，产品列表和价格数据正常，背景资源已随正式静态包加载
