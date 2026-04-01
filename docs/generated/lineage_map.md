# Lineage map

1. `event contract` -> `campaign planner / controller`
2. `campaign` -> `validated experiment request`
3. `validated experiment request` -> `promotion_service`
4. `promotion_service` -> `evidence_bundles.jsonl`
5. `evidence bundles + promoted candidates` -> `PromotedThesis` export
6. `PromotedThesis` -> `project.live.retriever / decision`
