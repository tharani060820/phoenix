// Logistics Resilience Network - Disruptions, Recoveries & Coordination Data
window.LRN_DISRUPTIONS = {
  "active_disruptions": [
    {
      "id": "DISR-2026-081",
      "title": "ROUTE 5 CLOSED",
      "code": "R05-CRITICAL",
      "severity": "CRITICAL",
      "badge_color": "red",
      "cause": "Multi-vehicle collision & chemical spill",
      "location": "Expressway Sector 5 (Mile 18)",
      "time": "14:32",
      "expected_duration": "3h 45m",
      "affected_route": "R05",
      "affected_vehicle": "V23",
      "impact": {
        "deliveries_affected": 18,
        "vehicles_affected": 4,
        "sla_breaches": 7,
        "estimated_penalty": 2450
      },
      "status": "RIPPLE ANALYSIS ACTIVE",
      "root_node": "R05",
      "direct_nodes": [
        "R05",
        "V23",
        "D1045",
        "D1021",
        "D1022",
        "D1023",
        "D1024",
        "D1025"
      ],
      "secondary_nodes": [
        "D1026",
        "D1027",
        "D1028",
        "D1029",
        "D1030",
        "C208",
        "C001",
        "C003",
        "C005",
        "V19"
      ]
    },
    {
      "id": "DISR-2026-082",
      "title": "CUSTOMER RESCHEDULE",
      "code": "D1045-WARNING",
      "severity": "WARNING",
      "badge_color": "orange",
      "cause": "Facility inspection delayed at AcroTech BioLabs",
      "location": "Customer C208 Receiving Dock",
      "time": "14:15",
      "expected_duration": "2h 00m",
      "affected_route": "R05",
      "affected_vehicle": "V23",
      "impact": {
        "deliveries_affected": 1,
        "vehicles_affected": 1,
        "sla_breaches": 1,
        "estimated_penalty": 420
      },
      "status": "RESCHEDULE WINDOW OPEN",
      "root_node": "D1045",
      "direct_nodes": [
        "D1045",
        "C208"
      ],
      "secondary_nodes": [
        "V23"
      ]
    },
    {
      "id": "DISR-2026-083",
      "title": "VEHICLE BREAKDOWN",
      "code": "V23-FAULT",
      "severity": "CRITICAL",
      "badge_color": "red",
      "cause": "Coolant manifold failure & power loss",
      "location": "Lat 11.0168, Long 76.9558 (No-Cellular Zone)",
      "time": "14:28",
      "expected_duration": "4h 15m",
      "affected_route": "R05",
      "affected_vehicle": "V23",
      "impact": {
        "deliveries_affected": 9,
        "vehicles_affected": 1,
        "sla_breaches": 5,
        "estimated_penalty": 1850
      },
      "status": "TELEMETRY LOST - SOS ACTIVE",
      "root_node": "V23",
      "direct_nodes": [
        "V23",
        "D1045",
        "D1021",
        "D1022"
      ],
      "secondary_nodes": [
        "R05",
        "C208",
        "C002"
      ]
    },
    {
      "id": "DISR-2026-084",
      "title": "WAREHOUSE DELAY",
      "code": "HUB-H02-BACKLOG",
      "severity": "MODERATE",
      "badge_color": "orange",
      "cause": "Automated Stacker Crane sensor calibration error",
      "location": "Warehouse Hub WH02 (Dock 4B-8)",
      "time": "13:50",
      "expected_duration": "1h 15m",
      "affected_route": "R04",
      "affected_vehicle": "V07",
      "impact": {
        "deliveries_affected": 14,
        "vehicles_affected": 3,
        "sla_breaches": 2,
        "estimated_penalty": 980
      },
      "status": "PARTITIONING RECOMMENDED",
      "root_node": "WH02",
      "direct_nodes": [
        "WH02",
        "R04",
        "R06"
      ],
      "secondary_nodes": [
        "V07",
        "V08",
        "D1039",
        "D1040"
      ]
    }
  ],
  "recovery_options": [
    {
      "id": "REC-01",
      "type": "REDIRECT",
      "title": "Redirect D1045 \u2192 Vehicle V27",
      "subtitle": "Dispatch standby fast-response sprinter V27 via alternate Highway Connector R07",
      "target_vehicle": "V27",
      "target_route": "R07",
      "target_delivery": "D1045",
      "feasibility": 95,
      "cost_saving": 350,
      "operational_cost": 45,
      "customer_impact": "Low",
      "disruption_score": 12,
      "overall_score": 94,
      "recovery_time_min": 4.5,
      "recommended": true,
      "badge": "AI Top Pick",
      "explanation": {
        "title": "WHY THIS RECOVERY?",
        "reasons": [
          "Vehicle V27 is currently idle and on standby within 3.2 km of transfer waypoint.",
          "Connector Route R07 operates with zero congestion and bypasses the Mile 18 closure entirely.",
          "Customer C208 Platinum SLA deadline (15:30) can be guaranteed with 12 minutes margin.",
          "Lowest estimated operational expenditure with zero auxiliary fleet dispatch fees.",
          "Minimal ripple effect: Eliminates downstream delivery cascade for remaining 4 scheduled drops."
        ],
        "confidence": 95,
        "constraints": [
          {
            "label": "Fleet Proximity",
            "value": "3.2 km (Optimal)",
            "status": "pass"
          },
          {
            "label": "Sprinter Payload Capacity",
            "value": "1,800 / 6,000 kg (Available)",
            "status": "pass"
          },
          {
            "label": "Cold-Chain Integrity",
            "value": "-80\u00b0C Cryo-Pod Verified",
            "status": "pass"
          },
          {
            "label": "Driver Shift Remaining",
            "value": "5.4 hrs on duty",
            "status": "pass"
          }
        ]
      }
    },
    {
      "id": "REC-02",
      "type": "REALLOCATE",
      "title": "Reallocate 4 deliveries from V23 \u2192 V19",
      "subtitle": "Dynamic load balancing with auxiliary van V19 crossing at Junction 12",
      "target_vehicle": "V19",
      "target_route": "R04",
      "target_delivery": "D1021-D1024",
      "feasibility": 88,
      "cost_saving": 220,
      "operational_cost": 85,
      "customer_impact": "Medium",
      "disruption_score": 18,
      "overall_score": 86,
      "recovery_time_min": 8.2,
      "recommended": false,
      "explanation": {
        "title": "WHY THIS RECOVERY?",
        "reasons": [
          "Van V19 has 42% remaining payload volume and shares 3 overlapping delivery zones.",
          "Saves $220 in SLA delay fines across 4 medium-priority commercial accounts.",
          "Requires 8.2 minutes physical handover and driver check-in.",
          "Acceptable minor delay (+15 mins) on V19's existing secondary stops."
        ],
        "confidence": 88,
        "constraints": [
          {
            "label": "Fleet Proximity",
            "value": "6.8 km",
            "status": "pass"
          },
          {
            "label": "Auxiliary Van Load",
            "value": "82% utilized after transfer",
            "status": "pass"
          },
          {
            "label": "Driver Shift Remaining",
            "value": "3.8 hrs on duty",
            "status": "pass"
          }
        ]
      }
    },
    {
      "id": "REC-03",
      "type": "RESCHEDULE",
      "title": "Move D1045 to 16:30",
      "subtitle": "Push delivery window by 60 mins with automated digital customer voucher and notification",
      "target_vehicle": "V23",
      "target_route": "R05",
      "target_delivery": "D1045",
      "feasibility": 92,
      "cost_saving": 80,
      "operational_cost": 25,
      "customer_impact": "Medium",
      "disruption_score": 24,
      "overall_score": 81,
      "recovery_time_min": 2.1,
      "recommended": false,
      "explanation": {
        "title": "WHY THIS RECOVERY?",
        "reasons": [
          "Zero physical vehicle movement needed; executed digitally within 2 minutes.",
          "Client C208 inspection team has tentatively accepted a 60-minute delivery buffer.",
          "Relieves immediate operational stress while tow truck clears Highway 45.",
          "Customer satisfaction penalty risk offset by automatic tier rebate."
        ],
        "confidence": 92,
        "constraints": [
          {
            "label": "Customer Approval",
            "value": "Pending confirmation (Auto-SLA)",
            "status": "warning"
          },
          {
            "label": "Perishability Expiry",
            "value": "Cryo battery holds 6.5h safe",
            "status": "pass"
          }
        ]
      }
    },
    {
      "id": "REC-04",
      "type": "PARTITION",
      "title": "Partition Route R05 cargo between Hub WH01 and WH03",
      "subtitle": "Split regional deliveries at cross-dock facility into two divergent radial routes",
      "target_vehicle": "V04 & V11",
      "target_route": "R02 & R08",
      "target_delivery": "Bulk Route R05",
      "feasibility": 84,
      "cost_saving": 190,
      "operational_cost": 115,
      "customer_impact": "Low",
      "disruption_score": 28,
      "overall_score": 78,
      "recovery_time_min": 12.0,
      "recommended": false,
      "explanation": {
        "title": "WHY THIS RECOVERY?",
        "reasons": [
          "High systemic resilience for large-scale disruptions involving >15 consignments.",
          "Completely isolates Central Sorting Hub WH02 bottleneck.",
          "Requires cross-dock coordination between two distinct terminal dispatchers."
        ],
        "confidence": 84,
        "constraints": [
          {
            "label": "Cross-Dock Readiness",
            "value": "Bay 3 Available in 10 mins",
            "status": "pass"
          },
          {
            "label": "Fuel Efficiency",
            "value": "-8% vs direct haul",
            "status": "warning"
          }
        ]
      }
    },
    {
      "id": "REC-05",
      "type": "DEFER",
      "title": "Defer non-perishable batches D1082 & D1089 to Evening Shift",
      "subtitle": "Hold standard-tier freight at warehouse staging area and prioritize cold-chain",
      "target_vehicle": "V17",
      "target_route": "R10",
      "target_delivery": "D1082, D1089",
      "feasibility": 90,
      "cost_saving": 50,
      "operational_cost": 10,
      "customer_impact": "High",
      "disruption_score": 35,
      "overall_score": 72,
      "recovery_time_min": 1.5,
      "recommended": false,
      "explanation": {
        "title": "WHY THIS RECOVERY?",
        "reasons": [
          "Free up vehicle carrying capacity for critical pharmaceutical items.",
          "Standard tier clients have contractual 24-hour delivery tolerance.",
          "Lowest implementation complexity."
        ],
        "confidence": 90,
        "constraints": [
          {
            "label": "Client Tier",
            "value": "Standard Tier (No instant penalty)",
            "status": "pass"
          },
          {
            "label": "Warehouse Staging Area",
            "value": "Available Bay 7",
            "status": "pass"
          }
        ]
      }
    }
  ],
  "intelligence": {
    "metrics": {
      "strategies_evaluated": 1842,
      "successful_recoveries": 1742,
      "learning_accuracy_pct": 94.7,
      "avg_recovery_time_min": 6.4,
      "total_cost_saved_usd": 482900,
      "incidents_prevented": 318
    },
    "strategy_success": [
      {
        "strategy": "Redirect",
        "success_rate": 94,
        "avg_time_min": 4.8,
        "cost_efficiency": 92,
        "color": "#10B981"
      },
      {
        "strategy": "Reallocate",
        "success_rate": 89,
        "avg_time_min": 7.5,
        "cost_efficiency": 85,
        "color": "#06B6D4"
      },
      {
        "strategy": "Reschedule",
        "success_rate": 86,
        "avg_time_min": 2.4,
        "cost_efficiency": 78,
        "color": "#8B5CF6"
      },
      {
        "strategy": "Partition",
        "success_rate": 82,
        "avg_time_min": 11.2,
        "cost_efficiency": 88,
        "color": "#F59E0B"
      },
      {
        "strategy": "Defer",
        "success_rate": 71,
        "avg_time_min": 1.8,
        "cost_efficiency": 64,
        "color": "#64748B"
      }
    ],
    "disruption_resilience_matrix": [
      {
        "disruption": "Road Closure",
        "preferred_strategy": "Redirect",
        "preference_score": 92,
        "secondary_strategy": "Reallocate",
        "recovery_speed": "Fast (4.2m)"
      },
      {
        "disruption": "Vehicle Breakdown",
        "preferred_strategy": "Reallocate",
        "preference_score": 88,
        "secondary_strategy": "Redirect",
        "recovery_speed": "Medium (7.8m)"
      },
      {
        "disruption": "Customer Reschedule",
        "preferred_strategy": "Reschedule",
        "preference_score": 95,
        "secondary_strategy": "Defer",
        "recovery_speed": "Instant (1.9m)"
      },
      {
        "disruption": "Warehouse Delay",
        "preferred_strategy": "Partition",
        "preference_score": 84,
        "secondary_strategy": "Redirect",
        "recovery_speed": "Medium (10.4m)"
      },
      {
        "disruption": "Weather Event",
        "preferred_strategy": "Defer",
        "preference_score": 79,
        "secondary_strategy": "Reschedule",
        "recovery_speed": "Fast (3.1m)"
      },
      {
        "disruption": "Driver Unavailable",
        "preferred_strategy": "Reallocate",
        "preference_score": 86,
        "secondary_strategy": "Redirect",
        "recovery_speed": "Fast (5.0m)"
      }
    ],
    "recovery_speed_trend": [
      {
        "month": "May 2026",
        "recovery_time_min": 21.4,
        "sla_breaches": 48,
        "accuracy": 74.2
      },
      {
        "month": "Jun 2026",
        "recovery_time_min": 17.8,
        "sla_breaches": 36,
        "accuracy": 79.5
      },
      {
        "month": "Jul 2026",
        "recovery_time_min": 14.1,
        "sla_breaches": 29,
        "accuracy": 84.1
      },
      {
        "month": "Aug 2026",
        "recovery_time_min": 10.5,
        "sla_breaches": 18,
        "accuracy": 89.6
      },
      {
        "month": "Sep 2026",
        "recovery_time_min": 8.2,
        "sla_breaches": 11,
        "accuracy": 92.4
      },
      {
        "month": "Oct 2026",
        "recovery_time_min": 6.4,
        "sla_breaches": 7,
        "accuracy": 94.7
      }
    ],
    "system_learnings": [
      {
        "tag": "FLEET PROXIMITY RULE",
        "rule": "Redirect strategies perform best when alternate vehicles are available within 5 km.",
        "impact": "+24% faster recovery time; 98% driver acceptance rate.",
        "derived_from": "428 expressway routing incidents in Q2-Q3 2026."
      },
      {
        "tag": "SLA THRESHOLD RULE",
        "rule": "Customer rescheduling is preferred when SLA risk remains below 20%.",
        "impact": "Zero financial penalty payout for standard and gold contractual tiers.",
        "derived_from": "612 dynamic delivery rescheduling events."
      },
      {
        "tag": "CASCADE SUPPRESSION",
        "rule": "Partitioning reduces ripple effects during high-volume disruptions (>15 deliveries).",
        "impact": "Suppressed multi-echelon warehouse spillover by 63% during peak hours.",
        "derived_from": "115 automated hub sorting delays analyzed."
      },
      {
        "tag": "OFFLINE MESH RESILIENCE",
        "rule": "Offline LoRa SOS telemetry allows zero-blindspot recovery even in rural & mountain tunnels.",
        "impact": "Reduced unacknowledged vehicle breakdown latency from 52 mins to 90 seconds.",
        "derived_from": "34 extreme dead-zone road incidents."
      }
    ]
  },
  "sos": {
    "vehicle": {
      "id": "V23",
      "driver": "Devon Miller",
      "vehicle_type": "Heavy Cargo Rig 18T",
      "status": "SIGNAL_LOST",
      "location": {
        "lat": 11.0168,
        "lng": 76.9558,
        "corridor": "Highway 45 Mile 18 / Western Ghats Pass"
      },
      "fault": "Vehicle Breakdown",
      "fault_detail": "Catastrophic Coolant Line Rupture - Cylinder Head Overheat (118\u00b0C)",
      "connectivity": {
        "cellular": {
          "name": "Cellular (4G/5G)",
          "status": "OFFLINE",
          "signal": "0 Bars (Dead Zone)",
          "icon": "x"
        },
        "wifi": {
          "name": "Industrial Wi-Fi",
          "status": "OFFLINE",
          "signal": "No AP in range",
          "icon": "x"
        },
        "lora_satellite": {
          "name": "LoRa 868MHz / Satellite SOS",
          "status": "ONLINE",
          "signal": "Direct Satellite Uplink Active",
          "icon": "check"
        }
      },
      "cargo": "Cryo-Vaccine Batch #CV-8820 (Sub-Zero -80\u00b0C)",
      "cargo_priority": "CRITICAL",
      "cargo_temp": "-79.2\u00b0C (Warning: Rising 0.1\u00b0C / 10m)"
    },
    "simulated_packet": {
      "vehicle_id": "V23",
      "fault": "BREAKDOWN",
      "priority": "CRITICAL",
      "timestamp": "14:42",
      "location": "11.0168, 76.9558",
      "battery_pct": 14,
      "engine_temp_c": 118,
      "mesh_hop_count": 2,
      "payload_bytes": 64,
      "crc_checksum": "0x9F3E8B"
    }
  },
  "coordination": {
    "plan_id": "LRN-2048",
    "title": "Emergency Reroute & Sprinter Handoff (V23 \u2192 V27)",
    "status": "IN_PROGRESS",
    "created_at": "14:34",
    "actions": [
      {
        "id": "ACT-1",
        "title": "Driver V27 notified",
        "detail": "Dispatched order via LRN Terminal App (Acknowledged)",
        "completed": true,
        "time": "14:35"
      },
      {
        "id": "ACT-2",
        "title": "Customer C208 notified",
        "detail": "WhatsApp & SMS sent to Priya Sharma (Read 14:36)",
        "completed": true,
        "time": "14:36"
      },
      {
        "id": "ACT-3",
        "title": "Route updated",
        "detail": "Corridor switched from R05 to alternate R07 connector",
        "completed": true,
        "time": "14:37"
      },
      {
        "id": "ACT-4",
        "title": "Delivery schedule updated",
        "detail": "Estimated delivery reset to 15:18 (SLA intact)",
        "completed": true,
        "time": "14:38"
      }
    ],
    "timeline": [
      {
        "time": "14:32",
        "event": "Disruption detected",
        "desc": "Highway 45 blocked due to major collision at Mile 18",
        "type": "critical"
      },
      {
        "time": "14:33",
        "event": "Ripple analysis completed",
        "desc": "18 deliveries flagged across 4 vehicles; $2,450 penalty risk",
        "type": "warning"
      },
      {
        "time": "14:34",
        "event": "Recovery generated",
        "desc": "AI Recovery Engine produced 5 ranked options; Redirect V27 ranked #1 (94/100)",
        "type": "ai"
      },
      {
        "time": "14:35",
        "event": "Operator approved",
        "desc": "Senior Dispatcher Capt. Alex Chen authorized Plan #LRN-2048",
        "type": "success"
      },
      {
        "time": "14:35",
        "event": "Driver notified",
        "desc": "Sarah Connor (V27) received turn-by-turn re-route via Route R07",
        "type": "success"
      },
      {
        "time": "14:36",
        "event": "Customer notified",
        "desc": "Automated update with live tracking link dispatched to AcroTech BioLabs",
        "type": "success"
      },
      {
        "time": "14:38",
        "event": "Recovery in progress",
        "desc": "Vehicle V27 en route to transfer waypoint; ETA 8 mins",
        "type": "info"
      }
    ],
    "driver_message": {
      "recipient": "Sarah Connor (Driver V27)",
      "phone": "+1 (555) 234-5678",
      "vehicle": "High-Speed Logistics Sprinter 4.5T",
      "route": "R07 Alternate Connector",
      "text": "Route R05 is currently unavailable. Delivery D1045 has been reassigned to Vehicle V27. Follow Route R07. Cryo-pod temperature must be maintained below -75\u00b0C. Waypoint transfer coordinates uploaded to navigation console.",
      "timestamp": "14:35",
      "status": "DELIVERED_READ"
    },
    "customer_message": {
      "recipient": "Priya Sharma (AcroTech BioLabs)",
      "phone": "+1 (555) 208-1208",
      "account_tier": "PLATINUM VIP",
      "order_id": "D1045",
      "text": "Your delivery has been rerouted due to an unexpected road disruption on Highway 45. Updated ETA: 15:18 (Within your contractual 15:30 SLA window). Dedicated Sprinter V27 is en route. Track live: lrn.io/track/D1045-C208",
      "timestamp": "14:36",
      "status": "DELIVERED_READ"
    }
  }
};
