# R3 UI Implementation Matrix

Implementation source of truth: `six-centers-design-review-r3-20260822-182819`.

| Page | R3 region | Current 5.4-r3 state | Gap | Final correction | Backend impact |
|---|---|---|---|---|---|
| Product list | Business filters, differentiated metrics, real media | Product cards and basic filters exist | Missing scenario filter and business status breakdown | Add high-value status metrics, category/scene filtering, type-aware highlight metrics | None |
| Product detail | Large gallery Hero, quick metrics, working tabs, main content + business rail | Small Hero, stacked sections, maintenance rail | Tabs absent; image and business actions underweighted | Rebuild first viewport and real tab panels; move maintenance data to secondary area | None |
| Software list | Logo/screenshot-led software asset cards | Generic initial-letter knowledge cards | Does not communicate software asset identity | Add software-specific cards, module/deployment/version metadata | None |
| Software detail | Screenshot Hero, module matrix, release/deployment facts, relations | Generic field/detail sections | Feature hierarchy and system visual are weak | Add screenshot-led Hero, metrics, working tabs, module matrix and relation groups | None |
| Algorithm list | Input/output and key performance | Generic knowledge cards | No algorithm flow or performance signal | Add algorithm-specific card metadata and metric summaries | None |
| Algorithm detail | Input -> process -> output, separated parameters and metrics | Generic descriptions and tables | No visual pipeline; parameter/metric hierarchy weak | Add pipeline, separate configuration and measured-result panels | None |
| Model list | Task type, core metrics, recommended hardware/scenes | Generic knowledge cards | Model performance is not first-class | Add model-specific cards with performance and task metadata | None |
| Model detail | Dark performance Hero, test evidence, structured I/O, deployment | Generic descriptions and metric list | Test evidence and structured contracts are visually weak | Add performance Hero, evidence strip, I/O tables and deployment/relationship panels | None |
| Scene list | Semantic scene image, capability/product/solution counts | Generic knowledge cards | Does not read as a business scenario catalog | Add image-led scene cards and relationship counts | None |
| Scene detail | Wide semantic Hero, pains/goals, capability matrix, node flow, recommendations | Basic image Hero and numbered lists | Flow/matrix/recommendation hierarchy missing | Add wide Hero, small-card pains/goals, real relation matrix, connected flow and recommendations | None |
| Solution list | Scene, tier, scope, core configuration | Generic knowledge cards | Does not read as deployable solutions | Add tier/scope/object/BOM metadata | None |
| Solution detail | Solution Hero, layered architecture, capability coverage, BOM/price | Generic descriptions and tables | Architecture and coverage are field-like | Add layered architecture, coverage table, composition relations and business-grade BOM | None |
| Global routing | URL/title/sidebar alignment | `/model-capabilities` evidence rendered Home | Route evidence invalid/stale | Revalidate route binding and regenerate evidence by DOM title, not filename | Frontend only |
| Counts | Product/API/report consistency | UI shows 17, prior report says 15; dashboard software is 0 | Seed minimum confused with current formal total; software omitted from dashboard API | Treat formal API/DB total as authoritative and add software metric | Small dashboard response fix |

## Acceptance rule

A page passes only when layout, field consumption, relationship presentation, visual hierarchy, interaction, responsive behavior, and route evidence match the frozen R3 intent. Field presence alone is not a pass.
