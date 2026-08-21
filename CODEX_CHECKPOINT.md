# FINAL OBJECTIVE
Deliver the V3.0 six-knowledge-center edition of 海智产品中心 from the frozen PRD baseline: 产品中心、软件中心、算法中心、模型能力中心、场景中心、方案中心. Reach `READY FOR PRODUCT/UI REVIEW` only after fields, same-page editing, relation drawers, PRICE_VIEW security, clean semantic seed data, responsive browser E2E, screenshots, and the final Word acceptance report pass. Preserve legacy port 80 and the currently accessible API 3.20 test version until the V3 replacement is built and verified.

# CURRENT PHASE
V3.0 second-round remediation, D7 model-capability center completion.

# CURRENT BUSINESS LOOP
V3 frozen product/UI implementation: ordinary users browse six centers read-only; product managers manage knowledge in the same pages; PRICE_VIEW controls all price fields.

# LAST SUCCESSFUL STEP
V3-D6: Extended algorithms with unique code, type, current version, localized lifecycle status, input/output summaries, structured core metrics, and applicability boundaries; added full create/edit/detail form and rendering support. Frontend build, backend/migration compile, and diff checks passed.

# CURRENT STEP
V3-D7: Complete the model-capability center frozen fields and workflows.

# NEXT EXACT STEP
Implement V3-D7 locally: extend model capabilities with unique code, model version, model category, function type, lifecycle status, structured metrics, input requirements, deployment requirements, recommended hardware, applicability and boundaries; expose list/detail/CRUD product-manager forms and localized read-only rendering; build/compile/check, update checkpoint, then continue to V3-D8 scene center.

# COMPLETED STEPS
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
- External `http://10.1.2.1:18080/` is blocked by firewall; port 443 is used as the temporary formal entry.
- HTTP `HEAD /` returns 405 because the static catch-all supports GET; GET root passed.
- Final Dify console re-login probe returned HTTP 401 `Invalid encrypted data` because Dify 1.16.1 requires client-side public-key encryption for the password field. This did not invalidate the previously passed Dify provider/application invocation or current healthy Dify runtime; no credential or runtime changes were made during the pause checkpoint.

# CURRENT ERRORS
- Port 443 still serves plain HTTP; a domain and trusted certificate have not been supplied.
- External product/UI review is pending; final responsive-browser closure and business acceptance status are intentionally paused.

# FIXES APPLIED
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
- `haizhi-hub-api`: running as hardened `haizhi-hub-api:3.20` on host port 18080; UID/GID 10001, read-only rootfs, all Linux capabilities dropped, no-new-privileges, connected to `haizhi-hub-net` and Dify `docker_default`.
- `haizhi-hub-gateway`: running on host port 443; connected to `haizhi-hub-net` and `haizhi-moodle-net`.
- `haizhi-moodle-db`: running and healthy with persistent named volume.
- `haizhi-moodle`: running after completed Moodle setup, mapped to host port 18082 with persistent application/data volumes.

# PORTS
- 80: legacy service, unchanged.
- 443: formal Nginx gateway serving HaiZhi at `/` and Moodle at `/moodle/`; plain HTTP pending domain/certificate.
- 18080: formal FastAPI/static frontend internal/new-service port.
- 18082: Moodle training service.
- PostgreSQL and Redis are internal Docker network only.

# DATABASE VERSION
- PostgreSQL 16 Alpine container. Production schema is at Alembic revision `d92a6b7c31e4`.

# APPLICATION VERSION
- Formal backend deployed: hardened `haizhi-hub-api:3.20`.
- Formal frontend built/deployed from `haizhi-hub-web:3.15` assets.
- Server project root `/opt/haizhi-product-hub` is not a Git worktree, so it has no branch or commit identifier; deployment is artifact/image based.
- Local workspace Git state: branch `master`, unborn repository with no `HEAD` commit. The entire `haizhi-product-hub` project is untracked/uncommitted in the parent workspace repository; all files are present on disk and were not deleted or rolled back.

# GIT STATE
- Server formal root: `NOT_A_GIT_WORKTREE`; branch and commit are not applicable.
- Local project branch: `feature/knowledge-centers-v3`.
- Local project baseline commit: `1f27d71496a17eea06344b45cbefdec81d43e6d5`.

# UNCOMMITTED CODE
- The local project is now Git-managed. At V3-D0 completion only `CODEX_CHECKPOINT.md` differs from the clean baseline commit; the change records the active V3 execution state.
- The formal server deployment remains artifact/image-managed at `/opt/haizhi-product-hub`; no V3 source or runtime has been deployed yet.

# DIFY STATUS
- PASS: Dify 1.16.1 core services are healthy; setup is finished; official OpenAI API Compatible plugin 0.0.62 is installed; protected HaiZhi Qwen3.6-27B model is active; chat app invocation reached the governed gateway and returned non-empty content; signature verification is restored to `true`.

# MOODLE STATUS
- PASS: persistent Moodle 5.0/MariaDB 11.4 stack, administrator login, representative course id 2, HaiZhi training association APIs, formal `/moodle/` publication, browser login, and authenticated course rendering pass.

# LLM STATUS
- PASS: Local OpenAI-compatible endpoint `http://10.1.2.4:6999`, model `/model/models/Qwen3.6-27B`; authenticated HaiZhi Gateway discovery/chat, normalization, Dify provider validation, and Dify application invocation all pass.

# EMBEDDING STATUS
- Deterministic 32-dimensional embedding, chunk persistence, and semantic retrieval endpoints deployed and verified.

# EXTERNAL BLOCKERS
- No public domain/certificate has been provided; 443 currently serves HTTP and cannot be marked as HTTPS PASS. Continue all other executable work.
- External product/UI review feedback is pending by explicit user request. This is a pause checkpoint, not a final `NOT READY` determination.

# DO NOT REPEAT
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
- While `NEXT EXACT STEP` is `WAITING_FOR_PRODUCT_UI_REVIEW`, do not add features/pages/fields/seed data, change UI, mutate formal data/runtime, stop services, or advance final acceptance.

# GATE A
IN PROGRESS: frontend/backend/PostgreSQL/Redis/MinIO/Docker/Alembic and formal reverse proxy pass; trusted TLS and final runtime regression remain pending.

# GATE B
PASS: product, catalog, scenario/solution, BOM/project, price, documents, and tender-support business loops pass through API and browser acceptance.

# GATE C
PASS: Dify application, AI Gateway/LLM governance, deterministic Embedding/RAG, and Moodle deployment/integration/browser launch pass.

# GATE D
PASS: RBAC, price audit, source/asset secret scan, authentication controls, security headers, network isolation, least-privilege API runtime, backup/restore, and controlled upgrade/rollback acceptance pass.
