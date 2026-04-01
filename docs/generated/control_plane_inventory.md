# Control plane inventory

## Campaign control
- canonical controller: `project.research.campaign_controller.CampaignController`
- operator adapter: `project.operator.campaign_engine.run_campaign`
- campaign contract: `project.research.campaign_contract.CampaignContract`

## Promotion control
- canonical service: `project.research.services.promotion_service.execute_promotion`
- live export: `project.research.live_export.export_promoted_theses_for_run`
- promoted thesis contract: `project.live.contracts.promoted_thesis.PromotedThesis`

## Planning control
- planner: `project.research.agent_io.campaign_planner.CampaignPlanner`
- validator: `project.research.experiment_engine.validate_agent_request`
- search intelligence: `project.research.search_intelligence.update_search_intelligence`
