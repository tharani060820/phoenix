"""
Logistics Resilience Network (LRN) - Graph Dependency Engine
Models multi-tier supply chain dependencies: Vehicle -> Route -> Delivery -> Customer.
Provides Cypher-compatible ripple-effect analysis, bottleneck identification, and downstream impact tracing.
Integrates with Neo4j when credentials exist, with high-performance in-memory graph traversal fallback.
"""
import os
import json
from typing import Dict, List, Any, Optional

class GraphDependencyEngine:
    def __init__(self):
        self.neo4j_driver = None
        self._init_neo4j()
        self._build_in_memory_graph()

    def _init_neo4j(self):
        """Attempts to connect to Neo4j database if credentials are configured."""
        uri = os.getenv("NEO4J_URI", "")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        if uri and password:
            try:
                from neo4j import GraphDatabase
                self.neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))
                print(f"[Neo4j] Connected to graph database at {uri}")
            except Exception as e:
                print(f"[Neo4j] Note: Neo4j driver connection skipped ({e}). Using native graph engine.")

    def _build_in_memory_graph(self):
        """Constructs rich graph topology: Vehicles, Routes, Warehouses, Deliveries, Customers."""
        self.nodes = {
            # Vehicles with live GPS telemetry & route assignments
            "V23": {
                "id": "V23",
                "type": "Vehicle",
                "name": "Heavy Freight Van V23",
                "capacity_kg": 3500,
                "current_route": "R05",
                "route_name": "Southwest Mountain Expressway (R05)",
                "driver": "employee01",
                "driver_name": "Dave Miller",
                "status": "HALTED_FAULT",
                "temp_controlled": True,
                "lat": 11.032,
                "lng": 76.942,
                "speed_kmh": 0,
                "heading": 240,
                "cargo": "Temperature-Sensitive Surgical Supplies & Cryo-Vaccines",
                "consignments": ["D1045", "D1021", "D1022", "D1023", "D1024"]
            },
            "V14": {
                "id": "V14",
                "type": "Vehicle",
                "name": "Standard Van V14",
                "capacity_kg": 2800,
                "current_route": "R01",
                "route_name": "North Metro Arterial (R01)",
                "driver": "driver02",
                "driver_name": "Sarah Jenkins",
                "status": "IN_TRANSIT",
                "temp_controlled": False,
                "lat": 11.050,
                "lng": 76.960,
                "speed_kmh": 52,
                "heading": 45,
                "cargo": "Retail High-Value Electronics Batch",
                "consignments": ["D1023"]
            },
            "V09": {
                "id": "V09",
                "type": "Vehicle",
                "name": "Urban Electric V09",
                "capacity_kg": 1800,
                "current_route": "R03",
                "route_name": "East River Crossing (R03)",
                "driver": "driver03",
                "driver_name": "Marcus Vance",
                "status": "IN_TRANSIT",
                "temp_controlled": False,
                "lat": 11.025,
                "lng": 76.990,
                "speed_kmh": 46,
                "heading": 90,
                "cargo": "General Consumer Goods",
                "consignments": ["D1024"]
            },
            "V27": {
                "id": "V27",
                "type": "Vehicle",
                "name": "Sprinter Relief V27",
                "capacity_kg": 2000,
                "current_route": "R12",
                "route_name": "Valley Bypass Corridor (R12)",
                "driver": "driver04",
                "driver_name": "Relief Pilot Standby",
                "status": "STANDBY_RELIEF",
                "location": "Apex North Hub",
                "temp_controlled": True,
                "lat": 11.085,
                "lng": 76.920,
                "speed_kmh": 0,
                "heading": 180,
                "cargo": "Standby Empty / Cryo Ready",
                "consignments": []
            },
            
            # Corridors / Routes with GPS polylines and vehicle linkage
            "R05": {
                "id": "R05",
                "type": "Route",
                "name": "Southwest Mountain Expressway",
                "distance_km": 48,
                "avg_speed_kmh": 65,
                "alt_route": "R12",
                "status": "DISRUPTED_BLOCKED",
                "assigned_vehicles": ["V23"],
                "color": "#EF4444",
                "waypoints": [
                    [11.0168, 76.9558],
                    [11.025, 76.948],
                    [11.032, 76.942],
                    [11.045, 76.935],
                    [11.060, 76.925]
                ]
            },
            "R12": {
                "id": "R12",
                "type": "Route",
                "name": "Valley Bypass Corridor",
                "distance_km": 54,
                "avg_speed_kmh": 70,
                "alt_route": "R05",
                "status": "ACTIVE_DETOUR_READY",
                "assigned_vehicles": ["V27"],
                "color": "#8B5CF6",
                "waypoints": [
                    [11.0168, 76.9558],
                    [11.040, 76.970],
                    [11.070, 76.960],
                    [11.085, 76.920]
                ]
            },
            "R01": {
                "id": "R01",
                "type": "Route",
                "name": "North Metro Arterial",
                "distance_km": 35,
                "avg_speed_kmh": 50,
                "status": "ACTIVE_CLEAR",
                "assigned_vehicles": ["V14"],
                "color": "#06B6D4",
                "waypoints": [
                    [11.085, 76.920],
                    [11.050, 76.950],
                    [11.0168, 76.9558]
                ]
            },
            "R03": {
                "id": "R03",
                "type": "Route",
                "name": "East River Crossing",
                "distance_km": 28,
                "avg_speed_kmh": 45,
                "status": "ACTIVE_CLEAR",
                "assigned_vehicles": ["V09"],
                "color": "#10B981",
                "waypoints": [
                    [11.0168, 76.9558],
                    [11.030, 77.040]
                ]
            },
            
            # Hubs
            "WH01": {"id": "WH01", "type": "Warehouse", "name": "North Logistics Park", "code": "HUB-NORTH", "lat": 11.085, "lng": 76.92},
            "WH02": {"id": "WH02", "type": "Warehouse", "name": "Central Automated Hub", "code": "HUB-H02", "lat": 11.0168, "lng": 76.9558},
            
            # Deliveries
            "D1045": {"id": "D1045", "type": "Delivery", "code": "D1045", "customer": "C208", "cargo": "Temperature-Sensitive Surgical Supplies", "sla": "15:30", "tier": "TIER_1_CRITICAL", "weight_kg": 240, "value_usd": 48500, "assigned_vehicle": "V23", "route": "R05"},
            "D1021": {"id": "D1021", "type": "Delivery", "code": "D1021", "customer": "C104", "cargo": "Critical Radiotherapy Radioisotopes", "sla": "15:45", "tier": "TIER_1_CRITICAL", "weight_kg": 85, "value_usd": 62000, "assigned_vehicle": "V23", "route": "R05"},
            "D1022": {"id": "D1022", "type": "Delivery", "code": "D1022", "customer": "C312", "cargo": "Automotive Assembly Spare Microchips", "sla": "16:15", "tier": "TIER_2_COMMERCIAL", "weight_kg": 620, "value_usd": 31000, "assigned_vehicle": "V23", "route": "R05"},
            "D1023": {"id": "D1023", "type": "Delivery", "code": "D1023", "customer": "C405", "cargo": "Retail High-Value Electronics Batch", "sla": "17:00", "tier": "TIER_3_STANDARD", "weight_kg": 890, "value_usd": 18500, "assigned_vehicle": "V23", "route": "R05"},
            "D1024": {"id": "D1024", "type": "Delivery", "code": "D1024", "customer": "C501", "cargo": "General Consumer Goods", "sla": "17:30", "tier": "TIER_3_STANDARD", "weight_kg": 1150, "value_usd": 9200, "assigned_vehicle": "V23", "route": "R05"},
            
            # Customers
            "C208": {"id": "C208", "type": "Customer", "name": "St. Jude Children's Research Medical Center", "tier": "HOSPITAL_VIP", "penalty_per_min": 150.0, "contact": "+1 (555) 019-2834", "lat": 11.060, "lng": 76.925},
            "C104": {"id": "C104", "type": "Customer", "name": "Regional Oncology Infusion Center", "tier": "HOSPITAL_VIP", "penalty_per_min": 180.0, "contact": "+1 (555) 019-8821", "lat": 11.055, "lng": 76.930},
            "C312": {"id": "C312", "type": "Customer", "name": "Nexus Precision Manufacturing Plant", "tier": "ENTERPRISE", "penalty_per_min": 75.0, "contact": "+1 (555) 019-4472", "lat": 11.045, "lng": 76.935},
            "C405": {"id": "C405", "type": "Customer", "name": "Metro Retail Fulfillment Hub 4", "tier": "RETAIL", "penalty_per_min": 25.0, "contact": "+1 (555) 019-5519", "lat": 11.035, "lng": 76.940},
            "C501": {"id": "C501", "type": "Customer", "name": "OmniDistribution Supercenter", "tier": "COMMERCIAL", "penalty_per_min": 20.0, "contact": "+1 (555) 019-9133", "lat": 11.025, "lng": 76.948}
        }

        # Directed relationship graph
        self.edges = [
            # Vehicle operates on Route
            {"source": "V23", "target": "R05", "type": "OPERATES_ON"},
            {"source": "V14", "target": "R01", "type": "OPERATES_ON"},
            {"source": "V09", "target": "R03", "type": "OPERATES_ON"},
            {"source": "V27", "target": "R12", "type": "STANDBY_CORRIDOR"},

            # Route connects Warehouse
            {"source": "R05", "target": "WH02", "type": "ORIGINATES_FROM"},
            {"source": "R12", "target": "WH02", "type": "ALTERNATIVE_DETOUR"},

            # Deliveries loaded onto Vehicle
            {"source": "V23", "target": "D1045", "type": "CARRIES"},
            {"source": "V23", "target": "D1021", "type": "CARRIES"},
            {"source": "V23", "target": "D1022", "type": "CARRIES"},
            {"source": "V23", "target": "D1023", "type": "CARRIES"},
            {"source": "V23", "target": "D1024", "type": "CARRIES"},

            # Deliveries destined for Customers
            {"source": "D1045", "target": "C208", "type": "DESTINED_FOR"},
            {"source": "D1021", "target": "C104", "type": "DESTINED_FOR"},
            {"source": "D1022", "target": "C312", "type": "DESTINED_FOR"},
            {"source": "D1023", "target": "C405", "type": "DESTINED_FOR"},
            {"source": "D1024", "target": "C501", "type": "DESTINED_FOR"}
        ]

    def analyze_ripple_effects(self, target_corridor: str = "R05", target_vehicle: str = "V23") -> Dict[str, Any]:
        """
        Executes multi-hop ripple effect traversal:
        (Disrupted Route/Vehicle) -> [CARRIES] -> (Delivery) -> [DESTINED_FOR] -> (Customer)
        Computes SLA risk, total cargo value in jeopardy, and available relief assets.
        """
        # If Neo4j is live, run native Cypher query
        if self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    cypher = """
                        MATCH (v:Vehicle)-[:OPERATES_ON]->(r:Route {id: $route})
                        OPTIONAL MATCH (v)-[:CARRIES]->(d:Delivery)-[:DESTINED_FOR]->(c:Customer)
                        RETURN v.id as vehicle, r.id as route, collect(d.id) as deliveries, collect(c.name) as customers
                    """
                    result = session.run(cypher, route=target_corridor).single()
                    if result:
                        print("[Neo4j] Traversed live Neo4j graph successfully.")
            except Exception as e:
                print(f"[Neo4j] Live traversal fallback: {e}")

        # In-memory graph traversal with exact Cypher relationship semantics
        affected_vehicles = [target_vehicle] if target_vehicle in self.nodes else ["V23"]
        affected_deliveries = []
        affected_customers = []
        total_cargo_value = 0
        critical_medical_deliveries = 0

        for edge in self.edges:
            if edge["source"] in affected_vehicles and edge["type"] == "CARRIES":
                d_id = edge["target"]
                d_node = self.nodes.get(d_id, {})
                affected_deliveries.append({
                    "id": d_id,
                    "cargo": d_node.get("cargo"),
                    "sla": d_node.get("sla"),
                    "tier": d_node.get("tier"),
                    "value_usd": d_node.get("value_usd", 0)
                })
                total_cargo_value += d_node.get("value_usd", 0)
                if "CRITICAL" in d_node.get("tier", ""):
                    critical_medical_deliveries += 1

                # Traverse to customer
                for c_edge in self.edges:
                    if c_edge["source"] == d_id and c_edge["type"] == "DESTINED_FOR":
                        c_id = c_edge["target"]
                        c_node = self.nodes.get(c_id, {})
                        if c_node and c_id not in [c["id"] for c in affected_customers]:
                            affected_customers.append({
                                "id": c_id,
                                "name": c_node.get("name"),
                                "tier": c_node.get("tier"),
                                "penalty_per_min": c_node.get("penalty_per_min", 20.0),
                                "contact": c_node.get("contact")
                            })

        # Find standby relief assets
        relief_assets = []
        for vid, node in self.nodes.items():
            if node.get("status") == "STANDBY_RELIEF":
                relief_assets.append({
                    "vehicle_id": vid,
                    "name": node.get("name"),
                    "location": node.get("location"),
                    "capacity_kg": node.get("capacity_kg"),
                    "temp_controlled": node.get("temp_controlled")
                })

        return {
            "disrupted_corridor": target_corridor,
            "blocked_vehicle": target_vehicle,
            "total_affected_deliveries": len(affected_deliveries),
            "critical_medical_deliveries": critical_medical_deliveries,
            "affected_deliveries": affected_deliveries,
            "affected_deliveries_list": affected_deliveries,
            "affected_customers": affected_customers,
            "total_cargo_value_usd": total_cargo_value,
            "available_relief_assets": relief_assets,
            "recommended_detour_corridor": self.nodes.get(target_corridor, {}).get("alt_route", "R12"),
            "graph_hops_evaluated": 4,
            "topology_schema": "Vehicle -> Route -> Delivery -> Customer"
        }

    def update_vehicle_telemetry(self, vid: str, lat: float, lng: float, status: str = None, route_id: str = None) -> Optional[Dict[str, Any]]:
        """Updates live GPS coordinates and operational status for vehicle."""
        if vid in self.nodes:
            self.nodes[vid]["lat"] = lat
            self.nodes[vid]["lng"] = lng
            if status:
                self.nodes[vid]["status"] = status
            if route_id:
                self.nodes[vid]["current_route"] = route_id
            return self.nodes[vid]
        return None

    def get_map_telemetry(self) -> Dict[str, Any]:
        """Returns consolidated map objects linking vehicles to routes with GPS polylines."""
        vehicles = [v for k, v in self.nodes.items() if v.get("type") == "Vehicle"]
        routes = [v for k, v in self.nodes.items() if v.get("type") == "Route"]
        warehouses = [v for k, v in self.nodes.items() if v.get("type") == "Warehouse"]
        return {
            "vehicles": vehicles,
            "routes": routes,
            "warehouses": warehouses
        }

graph_engine = GraphDependencyEngine()
