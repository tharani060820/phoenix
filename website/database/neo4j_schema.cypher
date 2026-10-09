// ==============================================================================
// Logistics Resilience Network (LRN) - Neo4j Graph Database Schema & Queries
// Graph-Based Adaptive Recovery System
// ==============================================================================

// 1. UNIQUE CONSTRAINTS & INDEXES
CREATE CONSTRAINT unique_warehouse_id IF NOT EXISTS FOR (w:Warehouse) REQUIRE w.id IS UNIQUE;
CREATE CONSTRAINT unique_route_id IF NOT EXISTS FOR (r:Route) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT unique_vehicle_id IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT unique_delivery_id IF NOT EXISTS FOR (d:Delivery) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT unique_customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE;

CREATE INDEX delivery_status_idx IF NOT EXISTS FOR (d:Delivery) ON (d.status);
CREATE INDEX vehicle_status_idx IF NOT EXISTS FOR (v:Vehicle) ON (v.status);
CREATE INDEX route_status_idx IF NOT EXISTS FOR (r:Route) ON (r.status);

// 2. GRAPH DATA SEEDING (SAMPLE CORRIDOR)
// Warehouses
MERGE (wh2:Warehouse {id: 'WH02', name: 'Central Automated Sorting Hub', code: 'HUB-H02', lat: 11.0168, lng: 76.9558, capacity: 25000});
MERGE (wh3:Warehouse {id: 'WH03', name: 'West Coastal Multi-Modal Terminal', code: 'HUB-WEST', lat: 10.9800, lng: 76.8800, capacity: 18000});

// Routes
MERGE (r5:Route {id: 'R05', name: 'Highway 45 / Expressway Sector 5', length_km: 54.0, status: 'BLOCKED'});
MERGE (r7:Route {id: 'R07', name: 'West-Central Connector (Alternate)', length_km: 58.5, status: 'ACTIVE'});

// Link Routes to Warehouses
MERGE (wh2)-[:ORIGINATES]->(r5);
MERGE (wh3)-[:ORIGINATES]->(r7);

// Vehicles
MERGE (v23:Vehicle {id: 'V23', driver: 'Devon Miller', type: 'Heavy Cargo Rig 18T', status: 'SIGNAL_LOST', lat: 11.0168, lng: 76.9558});
MERGE (v27:Vehicle {id: 'V27', driver: 'Sarah Connor', type: 'High-Speed Logistics Sprinter 4.5T', status: 'AVAILABLE_STANDBY', lat: 11.0042, lng: 76.9180});

MERGE (v23)-[:ASSIGNED_ROUTE]->(r5);
MERGE (v27)-[:ASSIGNED_ROUTE]->(r7);

// Customer C208
MERGE (c208:Customer {id: 'C208', name: 'AcroTech BioLabs', tier: 'PLATINUM', penalty_per_hour: 1200});

// Delivery D1045
MERGE (d1045:Delivery {
    id: 'D1045', 
    cargo: 'Cryo-Vaccine Batch #CV-8820', 
    priority: 'CRITICAL', 
    status: 'AT_RISK', 
    sla_deadline: '15:30',
    risk_score: 87
});

MERGE (d1045)-[:LOADED_ON]->(v23);
MERGE (d1045)-[:DESTINED_FOR]->(c208);
MERGE (d1045)-[:DISPATCHED_FROM]->(wh2);

// ==============================================================================
// 3. GRAPH TRAVERSAL ALGORITHMS FOR RIPPLE EFFECT ANALYSIS
// ==============================================================================

// Query A: Find all direct and secondary cascade entities when Route R05 is blocked
// Multi-hop path finding from disrupted route to affected customers
MATCH path = (r:Route {id: 'R05'})<-[:ASSIGNED_ROUTE]-(v:Vehicle)<-[:LOADED_ON]-(d:Delivery)-[:DESTINED_FOR]->(c:Customer)
RETURN 
    r.id AS DisruptedRoute,
    v.id AS BlockedVehicle,
    v.driver AS Driver,
    d.id AS AtRiskDelivery,
    d.priority AS CargoPriority,
    d.sla_deadline AS SLADeadline,
    c.id AS AffectedCustomer,
    c.tier AS CustomerTier,
    c.penalty_per_hour AS FinancialRiskPerHour;

// Query B: Downstream 2-Hop Ripple Cascade Detection
MATCH (r:Route {id: 'R05'})<-[:ASSIGNED_ROUTE]-(v:Vehicle)
MATCH (v)<-[:LOADED_ON]-(d:Delivery)
OPTIONAL MATCH (v)-[:SCHEDULED_FOR_NEXT]->(next_d:Delivery)
RETURN 
    count(DISTINCT d) AS DirectDeliveryImpact,
    count(DISTINCT next_d) AS SecondaryRippleImpact,
    collect(DISTINCT d.id) AS CriticalDeliveryIDs;

// Query C: AI Recovery Reroute Candidate Discovery
// Finds nearest standby vehicles with sufficient capacity and compatible route
MATCH (target:Delivery {id: 'D1045'})
MATCH (v_cand:Vehicle)
WHERE v_cand.status IN ['AVAILABLE_STANDBY', 'ONLINE'] 
  AND v_cand.id <> 'V23'
MATCH (v_cand)-[:ASSIGNED_ROUTE]->(r_alt:Route {status: 'ACTIVE'})
RETURN 
    v_cand.id AS RecommendedVehicle,
    v_cand.driver AS DriverName,
    v_cand.type AS VehicleType,
    r_alt.id AS AlternateRoute,
    r_alt.name AS CorridorName,
    point.distance(point({latitude: v_cand.lat, longitude: v_cand.lng}), point({latitude: 11.0168, longitude: 76.9558})) / 1000.0 AS DistanceKm
ORDER BY DistanceKm ASC
LIMIT 3;

// Query D: Apply Recovery Cypher Transaction (Atomic Edge Rewire)
MATCH (d:Delivery {id: 'D1045'})-[old_rel:LOADED_ON]->(v_old:Vehicle {id: 'V23'})
MATCH (v_new:Vehicle {id: 'V27'})
DELETE old_rel
CREATE (d)-[:LOADED_ON {reassigned_at: datetime(), recovery_plan: 'LRN-2048'}]->(v_new)
SET d.status = 'RECOVERED_IN_TRANSIT', d.risk_score = 12
RETURN d.id, v_new.id, d.status;
