# FINAL OBJECTIVE
Deliver the V3.0 six-knowledge-center edition of 海智产品中心 from the frozen PRD baseline: 产品中心、软件中心、算法中心、模型能力中心、场景中心、方案中心. Reach `READY FOR PRODUCT/UI REVIEW` only after fields, same-page editing, relation drawers, PRICE_VIEW security, clean semantic seed data, responsive browser E2E, screenshots, and the final Word acceptance report pass. Preserve legacy port 80 and the currently accessible API 3.20 test version until the V3 replacement is built and verified.

# CURRENT PHASE
SIX_CENTERS_FINAL_ACCEPTED

# CURRENT BUSINESS LOOP
R3 final freeze is approved as the implementation source of truth. Execute CHANGE -> BUILD -> TEST -> FIX -> RETEST -> CHECKPOINT -> NEXT across the six centers, then backup, deploy, production smoke, rollback verification, and final acceptance. Deferred AI/RAG/Moodle/project-workbench expansion remains out of scope.

# LAST SUCCESSFUL STEP
UIF-006: Created checksum-verified PostgreSQL and MinIO predeploy backups at `/opt/haizhi-product-hub/backups/ui-final-predeploy-20260823`, retained stopped rollback container `haizhi-hub-api-v54-uirollback-20260823`, switched formal port 18080/443 to immutable `haizhi-hub-api:5.5-ui-final` (image id prefix `ff6724a7593a`) without touching port 80, and passed formal health, exact static bundle, Alembic `4f6d8a2c1b90`, hardened runtime, six-center API/RBAC/PRICE_VIEW/relation/BOM acceptance, cleanup, and data counts `17/3/10/15/5/6`.

# CURRENT STEP
UIF-008_FINAL_ACCEPTANCE_PACKAGE_COMPLETE

# NEXT EXACT STEP
FINAL_STOP_CONDITION_SATISFIED_SIX_CENTERS_FINAL_ACCEPTED

# COMPLETED STEPS
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
- V3-D12 local execution of `tests/v3_price_security.py` could not start because both available Windows Python runtimes lack the installed SQLAlchemy dependency; the test itself compiles and must run inside the API image after deployment.
- External `http://10.1.2.1:18080/` is blocked by firewall; port 443 is used as the temporary formal entry.
- HTTP `HEAD /` returns 405 because the static catch-all supports GET; GET root passed.
- Final Dify console re-login probe returned HTTP 401 `Invalid encrypted data` because Dify 1.16.1 requires client-side public-key encryption for the password field. This did not invalidate the previously passed Dify provider/application invocation or current healthy Dify runtime; no credential or runtime changes were made during the pause checkpoint.
- V3-D14 integration runner attempt 1 failed because the immutable API image does not include `requests`; attempt 2 failed due the response key typo `accessToken`; the runner was corrected to installed `httpx` and `access_token`, then the complete integration regression passed.
- Moodle briefly became unavailable while correcting its health check because an overly broad replacement also changed the MariaDB probe. The MariaDB-native probe was restored, both containers were recreated against persistent volumes, and database/Moodle health plus gateway HTTP checks passed with course data preserved.

# CURRENT ERRORS
- No application-blocking errors remain.
- Port 443 still serves plain HTTP; a domain and trusted certificate have not been supplied.

# FIXES APPLIED
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
- Legacy: Python 2.7 + SQLite service managed by `haizhi-product-center`, port 80; preserve unchanged.
- Formal: FastAPI backend, Vue static frontend, PostgreSQL, Redis.

# CONTAINERS
- `haizhi-hub-postgres`: running.
- `haizhi-hub-redis`: running, password protected.
- `haizhi-hub-minio`: running with persistent named volume.
- `haizhi-hub-api`: running as hardened `haizhi-hub-api:5.5.1-ui-final` on host port 18080; UID/GID 10001, read-only rootfs, all Linux capabilities dropped, no-new-privileges, connected to `haizhi-hub-net` and Dify `docker_default`.
- `haizhi-hub-api-v55-uirollback-20260823`: stopped retained rollback point on immutable `haizhi-hub-api:5.5-ui-final`.
- `haizhi-hub-gateway`: running on host port 443; connected to `haizhi-hub-net` and `haizhi-moodle-net`.
- `haizhi-moodle-db`: running and healthy with persistent named volume.
- `haizhi-moodle`: running after completed Moodle setup, mapped to host port 18082 with persistent application/data volumes.
- `haizhi-hub-api-v41-20260822-022807`: stopped retained rollback point on immutable `haizhi-hub-api:4.1`; candidate, 4.0, and pre-V3 stopped containers were removed.

# PORTS
- 80: legacy service, unchanged.
- 443: formal Nginx gateway serving HaiZhi at `/` and Moodle at `/moodle/`; plain HTTP pending domain/certificate.
- 18080: formal FastAPI/static frontend internal/new-service port.
- 18082: Moodle training service.
- PostgreSQL and Redis are internal Docker network only.

# DATABASE VERSION
- PostgreSQL 16 Alpine container. Production schema is at Alembic revision `4f6d8a2c1b90`.

# APPLICATION VERSION
- Formal backend/frontend deployed: hardened immutable `haizhi-hub-api:5.5.1-ui-final` (image id `sha256:605485e91ca21d2f596d8f43eddd59ed33710ec4a25089a64cfee5db3a48e9b8`; static bundle `/assets/index-DlJGqRh-.js`).
- Server project root `/opt/haizhi-product-hub` is not a Git worktree, so it has no branch or commit identifier; deployment is artifact/image based.
- Local V3 project is a Git worktree on `feature/knowledge-centers-v3`.

# GIT STATE
- Server formal root: `NOT_A_GIT_WORKTREE`; branch and commit are not applicable.
- Local project branch: `feature/knowledge-centers-v3`.
- Local current commit: `HEAD` (PI-012 scoped production-readiness commit; resolve with `git rev-parse HEAD`).
- Local implementation acceptance commit: `afba5a0b7ef718a58d7c276b0bfb00bd5188932b`.
- Local acceptance report commit: `3c3bee2e5135665b7add2c13d57b6215d057256b`.

# UNCOMMITTED CODE
- Scoped production implementation is committed at `a2e54fc5b270174e38aea20d2c803ac79b5c93b6`; final checkpoint/report/package evidence is committed in the current `HEAD` (resolve with `git rev-parse HEAD`).
- Untracked design-review exports, render intermediates, extraction/build intermediates, and audit-only files remain intentionally excluded. They are user-owned or reproducible evidence and do not affect the deployed application.
- `frontend/tsconfig.tsbuildinfo` remains intentionally uncommitted as generated build metadata.
- Formal server deployment is artifact/image-managed at `/opt/haizhi-product-hub`; V3 source and immutable images are deployed.

# DIFY STATUS
- PASS: Dify 1.16.1 core services are healthy; setup is finished; official OpenAI API Compatible plugin 0.0.62 is installed; protected HaiZhi Qwen3.6-27B model is active; chat app invocation reached the governed gateway and returned non-empty content; signature verification is restored to `true`.

# MOODLE STATUS
- PASS: persistent Moodle 5.0/MariaDB 11.4 stack, administrator login, representative course id 2, HaiZhi training association APIs, formal `/moodle/` publication, browser login, and authenticated course rendering pass.

# LLM STATUS
- PASS: Local OpenAI-compatible endpoint `http://10.1.2.4:6999`, model `/model/models/Qwen3.6-27B`; authenticated HaiZhi Gateway discovery/chat, normalization, Dify provider validation, and Dify application invocation all pass.

# EMBEDDING STATUS
- Deterministic 32-dimensional embedding, chunk persistence, and semantic retrieval endpoints deployed and verified.

# EXTERNAL BLOCKERS
- None for six-center business acceptance.
- Production HTTPS remains an external launch dependency because no public domain/certificate has been provided; current formal review entry uses HTTP on port 443.

# DO NOT REPEAT
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
