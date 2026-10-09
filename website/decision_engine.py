"""
Logistics Resilience Network (LRN) - Decision Intelligence Engine
Generates and ranks recovery strategies:
1. redirect
2. reschedule
3. reallocate
4. partition
5. defer

Integrates with:
- Neo4j Graph Engine for multi-hop ripple-effect analysis
- SQL Adaptive Learning Engine for historical success weighting
- Multi-criteria scoring: Feasibility, Cost, Delay, Customer Impact
"""
import time
from typing import Dict, List, Any, Optional
from database.graph_engine import graph_engine
from database.adaptive_learning import adaptive_learning_engine

class DecisionIntelligenceEngine:
    def __init__(self):
        self.graph = graph_engine
        self.learner = adaptive_learning_engine

    def generate_recovery_strategies(
        self,
        disruption_event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Inputs disruption event -> queries graph ripple effects -> generates 5 recovery strategies
        -> scores each option -> applies adaptive learning weights -> returns ranked list with 'Recommended Action'.
        """
        corridor = disruption_event.get("affected_route", disruption_event.get("route", "R05"))
        vehicle_id = disruption_event.get("vehicleID", disruption_event.get("vehicle_id", "V23"))
        disruption_type = disruption_event.get("event", disruption_event.get("type", "ROAD_CLOSURE"))
        severity = disruption_event.get("priority", disruption_event.get("severity", "EMERGENCY"))
        is_hardware_sos = disruption_event.get("source") in ["LoRa/Satellite", "ESP32", "HARDWARE_SOS"]

        # 1. Query Graph Dependency Engine for Ripple Effects
        ripple = self.graph.analyze_ripple_effects(corridor, vehicle_id)

        # 2. Query SQL Adaptive Learning Engine for historical performance weights
        adaptive_stats = self.learner.get_strategy_performance()

        # 3. Formulate the 5 Canonical Recovery Strategies
        detour_route = ripple.get("recommended_detour_corridor", "R12")
        has_medical = ripple.get("critical_medical_deliveries", 0) > 0
        total_deliveries = ripple.get("total_affected_deliveries", 5)

        raw_strategies = [
            {
                "strategy_id": "STRAT-REDIRECT",
                "strategy": "redirect",
                "title": f"Dynamic Corridor Reroute (Via {detour_route} Valley Bypass)",
                "action_type": "Route Redirection",
                "description": f"Divert transit flow via alternate arterial corridor {detour_route}. Bypasses blocked sector entirely (+14 km, +18m transit time), preserving 100% of deliveries on-board without vehicle swap.",
                "feasibility_pct": 94 if disruption_type != "VEHICLE_FAULT" else 45,
                "cost_usd": 380.0,
                "delay_minutes": 18,
                "delay_mitigated_min": 45,
                "customer_impact": "LOW",
                "customer_impact_description": "Deliveries arrive within 20m of original SLA. Hospital VIPs alerted of updated GPS trace.",
                "sla_preservation_pct": 96 if disruption_type != "VEHICLE_FAULT" else 30,
                "assigned_asset": vehicle_id,
                "detour_corridor": detour_route
            },
            {
                "strategy_id": "STRAT-REALLOCATE",
                "strategy": "reallocate",
                "title": "Cross-Dock Fleet Relief (Dispatch Sprinter V27)",
                "action_type": "Asset Reallocation",
                "description": "Mobilize standby climate-controlled Sprinter V27 from Apex North Hub. Rendezvous at Mile 14 waypoint for cross-dock transfer of temperature-sensitive medical cargo (D1045, D1021).",
                "feasibility_pct": 92 if (disruption_type == "VEHICLE_FAULT" or is_hardware_sos) else 88,
                "cost_usd": 760.0,
                "delay_minutes": 12,
                "delay_mitigated_min": 65,
                "customer_impact": "MINIMAL",
                "customer_impact_description": "Guarantees zero cold-chain degradation for St. Jude Medical and Regional Oncology Center.",
                "sla_preservation_pct": 98,
                "assigned_asset": "V27 (Sprinter Relief)",
                "detour_corridor": detour_route
            },
            {
                "strategy_id": "STRAT-RESCHEDULE",
                "strategy": "reschedule",
                "title": "Dynamic Window Recalibration & SLA Tiering",
                "action_type": "Schedule Recalibration",
                "description": f"Retain current vehicle on cleared lanes after emergency clearance. Recalibrate delivery time windows for Tier 2 and Tier 3 commercial customers (C312, C405, C501) with automated SMS notifications.",
                "feasibility_pct": 82,
                "cost_usd": 140.0,
                "delay_minutes": 42,
                "delay_mitigated_min": 25,
                "customer_impact": "MEDIUM",
                "customer_impact_description": "Commercial recipients delayed by ~45m; hospital shipments may slip into grace period.",
                "sla_preservation_pct": 74,
                "assigned_asset": vehicle_id,
                "detour_corridor": corridor
            },
            {
                "strategy_id": "STRAT-PARTITION",
                "strategy": "partition",
                "title": "Consignment Load Partitioning & Multi-Courier Handover",
                "action_type": "Consignment Partition",
                "description": "Split cargo at Sector 4 staging depot: hot-transfer critical hospital medical packages to rapid urban courier, while holding commercial pallets for subsequent consolidated dispatch.",
                "feasibility_pct": 78,
                "cost_usd": 540.0,
                "delay_minutes": 26,
                "delay_mitigated_min": 32,
                "customer_impact": "LOW_TO_MEDIUM",
                "customer_impact_description": "Critical shipments on time; secondary freight delivered in evening wave.",
                "sla_preservation_pct": 86,
                "assigned_asset": "V23 + Urban Courier 04",
                "detour_corridor": detour_route
            },
            {
                "strategy_id": "STRAT-DEFER",
                "strategy": "defer",
                "title": "Controlled Transit Hold & Next-Shift Deferral",
                "action_type": "Shipment Deferral",
                "description": "Defer delivery of non-urgent freight consignments to next scheduled morning dispatch (T+24h) to avoid emergency overtime surcharges.",
                "feasibility_pct": 60 if not has_medical else 25,
                "cost_usd": 50.0,
                "delay_minutes": 720,
                "delay_mitigated_min": 0,
                "customer_impact": "HIGH",
                "customer_impact_description": "High risk of SLA breach penalty for high-value clients. Not acceptable for surgical cargo.",
                "sla_preservation_pct": 20,
                "assigned_asset": "Held in Transit Depot",
                "detour_corridor": "NONE"
            }
        ]

        # 4. Multi-Criteria Scoring with Adaptive Learning Weighting
        scored_strategies = []
        for s in raw_strategies:
            strat_key = s["strategy"]
            hist = adaptive_stats.get(strat_key, {})
            adaptive_multiplier = hist.get("adaptive_multiplier", 1.0)
            hist_success_pct = hist.get("success_percentage", "70%")
            deployments = hist.get("total_deployments", 0)

            # Component normalized weights (0-100 scale)
            feasibility_score = s["feasibility_pct"] * 0.35
            delay_score = (max(0, 100 - (s["delay_minutes"] * 1.5))) * 0.30
            cost_efficiency = (max(0, 100 - (s["cost_usd"] / 10.0))) * 0.15
            customer_retention = (100 if s["customer_impact"] == "MINIMAL" else (85 if s["customer_impact"] == "LOW" else (50 if s["customer_impact"] == "MEDIUM" else 20))) * 0.20

            raw_composite = feasibility_score + delay_score + cost_efficiency + customer_retention
            
            # Special domain rule: If vehicle has mechanical fault or hardware SOS, redirecting the same broken vehicle is penalized
            if (disruption_type == "VEHICLE_FAULT" or is_hardware_sos) and strat_key == "redirect":
                raw_composite *= 0.55
            elif (disruption_type == "VEHICLE_FAULT" or is_hardware_sos) and strat_key == "reallocate":
                raw_composite *= 1.25

            # Apply SQL Adaptive Learning Boost
            final_score = round(min(99.4, raw_composite * adaptive_multiplier), 1)

            s["scores"] = {
                "feasibility": s["feasibility_pct"],
                "cost_usd": s["cost_usd"],
                "delay_minutes": s["delay_minutes"],
                "delay_mitigated_min": s["delay_mitigated_min"],
                "customer_impact": s["customer_impact"],
                "sla_preservation_pct": s["sla_preservation_pct"],
                "raw_base_score": round(raw_composite, 1),
                "adaptive_learning_multiplier": adaptive_multiplier,
                "adaptive_boost_pct": f"+{int((adaptive_multiplier - 1.0) * 100)}%" if adaptive_multiplier >= 1.0 else f"{int((adaptive_multiplier - 1.0) * 100)}%",
                "historical_success_rate": hist_success_pct,
                "historical_deployments": deployments,
                "composite_score": final_score
            }
            scored_strategies.append(s)

        # 5. Rank strategies by composite_score descending
        ranked_strategies = sorted(scored_strategies, key=lambda x: x["scores"]["composite_score"], reverse=True)

        # 6. Flag top option as "Recommended Action"
        for idx, item in enumerate(ranked_strategies):
            item["rank"] = idx + 1
            item["is_recommended"] = (idx == 0)
            if idx == 0:
                item["recommendation_badge"] = "★ RECOMMENDED ACTION"
                item["ai_reasoning"] = (
                    f"Selected as the optimal recovery action with highest composite resilience score ({item['scores']['composite_score']}/100). "
                    f"Maintains {item['scores']['sla_preservation_pct']}% SLA compliance while mitigating {item['scores']['delay_mitigated_min']} minutes of operational delay. "
                    f"Reinforced by SQL adaptive learning with a {item['scores']['adaptive_boost_pct']} multiplier based on {item['scores']['historical_deployments']} successful deployments."
                )

        return {
            "disruption_id": disruption_event.get("id", "DISR-LIVE"),
            "target_corridor": corridor,
            "target_vehicle": vehicle_id,
            "disruption_type": disruption_type,
            "severity": severity,
            "is_hardware_sos": is_hardware_sos,
            "ripple_effects": ripple,
            "ranked_strategies": ranked_strategies,
            "recommended_action": ranked_strategies[0] if ranked_strategies else None,
            "adaptive_learning_engine_version": "2.4-SQL-ONLINE",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

decision_engine = DecisionIntelligenceEngine()
