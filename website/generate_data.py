import json
import random

# Fixed seeds for deterministic realistic mock data
random.seed(42)

warehouses = [
    {
        "id": "WH01",
        "name": "North Metro Logistics Park",
        "code": "HUB-NORTH",
        "city": "Metro North",
        "lat": 11.0850,
        "lng": 76.9200,
        "capacity_pallets": 15000,
        "current_load": 12450,
        "status": "OPERATIONAL",
        "health": "HEALTHY",
        "outbound_routes": ["R01", "R02", "R03"]
    },
    {
        "id": "WH02",
        "name": "Central Automated Sorting Hub",
        "code": "HUB-H02",
        "city": "Central Metro",
        "lat": 11.0168,
        "lng": 76.9558,
        "capacity_pallets": 25000,
        "current_load": 23800,
        "status": "DELAYED",
        "health": "DISRUPTED",
        "outbound_routes": ["R04", "R05", "R06"]
    },
    {
        "id": "WH03",
        "name": "West Coastal Multi-Modal Terminal",
        "code": "HUB-WEST",
        "city": "West Port",
        "lat": 10.9800,
        "lng": 76.8800,
        "capacity_pallets": 18000,
        "current_load": 14200,
        "status": "OPERATIONAL",
        "health": "HEALTHY",
        "outbound_routes": ["R07", "R08"]
    },
    {
        "id": "WH04",
        "name": "East Express Air Freight Gateway",
        "code": "HUB-EAST",
        "city": "Airport Industrial Zone",
        "lat": 11.0300,
        "lng": 77.0400,
        "capacity_pallets": 12000,
        "current_load": 9800,
        "status": "OPERATIONAL",
        "health": "HEALTHY",
        "outbound_routes": ["R09"]
    },
    {
        "id": "WH05",
        "name": "South Regional Distribution Center",
        "code": "HUB-SOUTH",
        "city": "South Valley",
        "lat": 10.9100,
        "lng": 76.9900,
        "capacity_pallets": 16000,
        "current_load": 13100,
        "status": "OPERATIONAL",
        "health": "HEALTHY",
        "outbound_routes": ["R10"]
    }
]

routes = [
    {
        "id": "R01",
        "name": "Northern Ring Arterial",
        "warehouse_id": "WH01",
        "length_km": 42.5,
        "avg_speed_kmh": 65,
        "congestion_level": "LOW",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R02"
    },
    {
        "id": "R02",
        "name": "North-East Bypass Corridor",
        "warehouse_id": "WH01",
        "length_km": 48.0,
        "avg_speed_kmh": 70,
        "congestion_level": "LOW",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R01"
    },
    {
        "id": "R03",
        "name": "Grand Trunk North Express",
        "warehouse_id": "WH01",
        "length_km": 36.2,
        "avg_speed_kmh": 58,
        "congestion_level": "MODERATE",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R04"
    },
    {
        "id": "R04",
        "name": "Central Inner Ring Road",
        "warehouse_id": "WH02",
        "length_km": 28.4,
        "avg_speed_kmh": 45,
        "congestion_level": "MODERATE",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R05"
    },
    {
        "id": "R05",
        "name": "Highway 45 / Expressway Sector 5",
        "warehouse_id": "WH02",
        "length_km": 54.0,
        "avg_speed_kmh": 0,
        "congestion_level": "BLOCKED",
        "status": "BLOCKED",
        "health": "DISRUPTED",
        "alt_route": "R07",
        "incident": "Major 3-vehicle pileup at Mile 18. Both lanes closed."
    },
    {
        "id": "R06",
        "name": "Industrial Spur 6B",
        "warehouse_id": "WH02",
        "length_km": 31.8,
        "avg_speed_kmh": 52,
        "congestion_level": "LOW",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R04"
    },
    {
        "id": "R07",
        "name": "West-Central Connector (Alternate to R05)",
        "warehouse_id": "WH03",
        "length_km": 58.5,
        "avg_speed_kmh": 68,
        "congestion_level": "LOW",
        "status": "ACTIVE",
        "health": "AI_PREDICTION",
        "alt_route": "R05"
    },
    {
        "id": "R08",
        "name": "Coastal Freight Parkway",
        "warehouse_id": "WH03",
        "length_km": 64.2,
        "avg_speed_kmh": 72,
        "congestion_level": "LOW",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R07"
    },
    {
        "id": "R09",
        "name": "Air Cargo Link Expressway",
        "warehouse_id": "WH04",
        "length_km": 38.0,
        "avg_speed_kmh": 75,
        "congestion_level": "LOW",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R06"
    },
    {
        "id": "R10",
        "name": "Southern Logistics Highway",
        "warehouse_id": "WH05",
        "length_km": 52.1,
        "avg_speed_kmh": 60,
        "congestion_level": "MODERATE",
        "status": "ACTIVE",
        "health": "HEALTHY",
        "alt_route": "R08"
    }
]

drivers = [
    ("V01", "Marcus Reid", "Electric 7.5T Hauler", "R01", 94, "ONLINE"),
    ("V02", "Elena Rostova", "Semi-Trailer Class 8", "R01", 88, "ONLINE"),
    ("V03", "Karthik Raja", "Refrigerated Van 3.5T", "R02", 91, "ONLINE"),
    ("V04", "David O'Connor", "Heavy Freight 12T", "R02", 82, "ONLINE"),
    ("V05", "Amara Diallo", "Electric Box Van", "R03", 79, "ONLINE"),
    ("V06", "Hiroshi Tanaka", "Urban Delivery Truck", "R03", 95, "ONLINE"),
    ("V07", "Sofia Mendez", "Curtain-sider 10T", "R04", 87, "ONLINE"),
    ("V08", "Vikram Patel", "Medium Flatbed 5T", "R04", 76, "ONLINE"),
    ("V09", "Chloe Dubois", "Reefer Sprinter 3.5T", "R04", 89, "ONLINE"),
    ("V10", "Tariq Mansoor", "Autonomous Electric 8T", "R06", 96, "ONLINE"),
    ("V11", "Lucas Becker", "Heavy Freight 16T", "R06", 84, "ONLINE"),
    ("V12", "Ananya Deshmukh", "Express Sprinter Van", "R01", 92, "ONLINE"),
    ("V13", "Gabriel Santos", "Medium Box Truck", "R08", 85, "ONLINE"),
    ("V14", "Zoe Chen", "Electric Urban Courier", "R08", 78, "ONLINE"),
    ("V15", "Mateo Rossi", "Heavy Articulated 24T", "R09", 93, "ONLINE"),
    ("V16", "Fatima Al-Sayed", "Temperature-Controlled 6T", "R09", 89, "ONLINE"),
    ("V17", "Lars Lindqvist", "Multi-Axle Carrier", "R10", 81, "ONLINE"),
    ("V18", "Grace Hopper", "Medium Cargo Van", "R10", 87, "ONLINE"),
    ("V19", "Marcus Vance", "Fast Response Sprinter 4T", "R04", 94, "ONLINE"),
    ("V20", "Devon Miller", "Heavy Cargo Rig 18T", "R05", 14, "SIGNAL_LOST")
]

# We need V23 and V27 specifically! Let's make V20 into V23 and add V27
vehicles = []
for vid, driver, vtype, route, bat, status in drivers:
    actual_id = vid
    if vid == "V20":
        actual_id = "V23"  # The breakdown truck from prompt
    v_obj = {
        "id": actual_id,
        "driver": driver,
        "type": vtype,
        "assigned_route": route,
        "battery_pct": bat,
        "status": status,
        "health": "DISRUPTED" if actual_id == "V23" else "HEALTHY",
        "current_load_kg": 4200 if actual_id == "V23" else random.randint(2100, 7500),
        "capacity_kg": 8500,
        "lat": 11.0168 if actual_id == "V23" else round(11.0000 + random.uniform(-0.15, 0.15), 4),
        "lng": 76.9558 if actual_id == "V23" else round(76.9500 + random.uniform(-0.15, 0.15), 4),
        "speed_kmh": 0 if actual_id == "V23" else random.randint(48, 74),
        "signal": "LOST" if actual_id == "V23" else "STRONG_5G",
        "telemetry": {
            "engine_temp_c": 118 if actual_id == "V23" else 88,
            "tire_pressure_psi": 29 if actual_id == "V23" else 36,
            "fuel_liters": 18 if actual_id == "V23" else 110,
            "lora_status": "MESH_BEACON_ACTIVE" if actual_id == "V23" else "STANDBY"
        }
    }
    vehicles.append(v_obj)

# Add V27 (the designated AI recovery redirect vehicle!)
vehicles.append({
    "id": "V27",
    "driver": "Sarah Connor",
    "type": "High-Speed Logistics Sprinter 4.5T",
    "assigned_route": "R07",
    "battery_pct": 92,
    "status": "AVAILABLE_STANDBY",
    "health": "AI_PREDICTION",
    "current_load_kg": 1800,
    "capacity_kg": 6000,
    "lat": 11.0042,
    "lng": 76.9180,
    "speed_kmh": 55,
    "signal": "STRONG_5G",
    "telemetry": {
        "engine_temp_c": 86,
        "tire_pressure_psi": 36,
        "fuel_liters": 140,
        "lora_status": "CONNECTED"
    }
})

# 50 realistic customers
customer_names = [
    "AcroTech BioLabs", "Zenith Pharma Logistics", "Global Core Electronics", "Apex Precision Aerospace",
    "OmniHealth Diagnostics", "NovaTech Cloud Systems", "AeroDynamics Corp", "Nexus Energy Grids",
    "Vanguard Robotics", "Quantum Sensor Tech", "Orion Medical Devices", "Titan Heavy Machinery",
    "BlueWater Biotech", "Silicon Valley Components", "TerraFirma Agritech", "Hyperion Defense Systems",
    "Starlight Optics", "Crestview Laboratories", "Pinnacle Semiconductor", "Kinetix Automations",
    "Synapse Neural Tech", "Falcon Global Cargo", "Solstice Renewable Labs", "Pulse Dynamics",
    "Cyberdine Logistics", "Matrix Cellular Networks", "Helios Solar Tech", "Astraea Scientific",
    "BioGenix Vaccines", "Echo Marine Systems", "Vertex Microchips", "Lumina Fiber Systems",
    "Cascade Industrial Chemical", "Optima Health Supplies", "Prism High-Tech Glass", "Aegis Secure Freight",
    "Horizon Power Systems", "Stratus Telematics", "NorthStar Precision", "Cobalt EV Batteries",
    "Aura Clean Technologies", "Ion Energy Storage", "Synthetix Biofab", "Pioneer Satellite Comms",
    "DeepSea Robotic Mining", "Genesis Clinical Trials", "Valence ChemLab", "Vector Space Instruments",
    "Dynamix Drone Systems", "AeroSpace Tech Hub"
]

customers = []
for i in range(1, 51):
    cid = f"C{i:03d}"
    if i == 208 or i == 8: # make C208 specially configured
        cid = "C208"
        cname = "AcroTech BioLabs (Priya Sharma, Dir. Clinical Ops)"
        ctier = "PLATINUM"
        cpenalty = 1200
    else:
        cname = customer_names[i-1] if i-1 < len(customer_names) else f"Enterprise Client #{i}"
        ctier = "PLATINUM" if i % 4 == 0 else ("GOLD" if i % 2 == 0 else "STANDARD")
        cpenalty = 800 if ctier == "PLATINUM" else (450 if ctier == "GOLD" else 200)
    
    customers.append({
        "id": cid,
        "name": cname,
        "tier": ctier,
        "penalty_per_hour": cpenalty,
        "phone": f"+1 (555) {200+i:03d}-{1000+i:04d}",
        "email": f"ops@{cid.lower()}.logistics.net",
        "address": f"{100 + i * 14} Technology Parkway, Industrial Sector {((i % 7) + 1)}",
        "lat": round(11.0100 + (random.uniform(-0.12, 0.12)), 4),
        "lng": round(76.9500 + (random.uniform(-0.12, 0.12)), 4)
    })

# 100 Deliveries D1001 - D1100
deliveries = []
commodities = [
    ("Cryo-Vaccine Cargo", "CRITICAL", 3500),
    ("Cardiac Stent Consignment", "CRITICAL", 2800),
    ("Semiconductor Lithography Wafers", "HIGH", 4200),
    ("Autonomous Drone Sensor Assembly", "HIGH", 1800),
    ("Automotive EV Inverter Spares", "NORMAL", 950),
    ("Industrial Robotic Actuators", "HIGH", 2100),
    ("Clinical Laboratory Reagents", "CRITICAL", 1600),
    ("Aerospace Titanium Fasteners", "NORMAL", 1100),
    ("Fiber-Optic Multiplexers", "NORMAL", 850),
    ("Precision Calibration Tools", "NORMAL", 600)
]

# Ensure D1045 is specifically assigned to V23, R05, WH02, C208
for i in range(1, 101):
    did = f"D{1000+i}"
    cargo, priority, val = random.choice(commodities)
    
    if did == "D1045":
        cargo = "Cryo-Vaccine Batch #CV-8820 (Sub-Zero -80°C)"
        priority = "CRITICAL"
        assigned_v = "V23"
        assigned_r = "R05"
        assigned_wh = "WH02"
        assigned_c = "C208"
        status = "AT_RISK"
        health = "DISRUPTED"
        sla_deadline = "15:30"
        projected_eta = "17:45"
        risk_score = 87
    elif did in ["D1021", "D1022", "D1023", "D1024", "D1025", "D1026", "D1027", "D1028", "D1029", "D1030", 
                 "D1031", "D1032", "D1033", "D1034", "D1035", "D1036", "D1037", "D1038"]:
        # Deliveries directly affected by Route 5 / V23 breakdown! (18 deliveries)
        assigned_v = "V23" if i % 2 == 0 else random.choice(["V07", "V08", "V09"])
        assigned_r = "R05"
        assigned_wh = "WH02"
        assigned_c = customers[i % len(customers)]["id"]
        status = "AT_RISK"
        health = "DISRUPTED" if assigned_v == "V23" else "SECONDARY_RIPPLE"
        sla_deadline = f"{14 + (i%3)}:{15 + (i*5)%45:02d}"
        projected_eta = f"{16 + (i%2)}:{30 + (i*3)%30:02d}"
        risk_score = random.randint(72, 94)
    elif i in [39, 40, 41, 42, 43, 44, 46, 47, 48]: # secondary ripple deliveries
        assigned_v = "V19" if i % 2 == 0 else "V09"
        assigned_r = "R04"
        assigned_wh = "WH02"
        assigned_c = customers[i % len(customers)]["id"]
        status = "SECONDARY_RIPPLE"
        health = "SECONDARY_RIPPLE"
        sla_deadline = "16:45"
        projected_eta = "17:35"
        risk_score = random.randint(55, 78)
    else:
        assigned_wh = random.choice(warehouses)["id"]
        assigned_r = random.choice([r["id"] for r in routes if r["id"] != "R05"])
        assigned_v = random.choice([v["id"] for v in vehicles if v["id"] != "V23"])
        assigned_c = customers[i % len(customers)]["id"]
        status = "IN_TRANSIT" if i % 5 != 0 else "ON_SCHEDULE"
        health = "HEALTHY"
        sla_deadline = f"{15 + (i%4)}:{10 + (i*7)%50:02d}"
        projected_eta = f"{15 + (i%4)}:{5 + (i*7)%50:02d}"
        risk_score = random.randint(5, 22)
        
    deliveries.append({
        "id": did,
        "title": cargo,
        "priority": priority,
        "value_usd": val,
        "warehouse_id": assigned_wh,
        "route_id": assigned_r,
        "vehicle_id": assigned_v,
        "customer_id": assigned_c,
        "status": status,
        "health": health,
        "sla_deadline": sla_deadline,
        "projected_eta": projected_eta,
        "risk_score": risk_score,
        "temp_controlled": priority == "CRITICAL",
        "recommended_action": "Redirect to V27 via R07" if did == "D1045" else ("Reallocate to V19" if health != "HEALTHY" else "Continue Current Route")
    })

# Build Graph Nodes & Edges
# To keep D3 visualization crisp, fast, and legible, we create the full interconnected graph:
# All 5 Warehouses, All 10 Routes, 20 Vehicles, Key Deliveries (e.g. 35 core deliveries including all disrupted & ripple ones), and Key Customers!
graph_nodes = []
graph_edges = []
node_ids = set()

def add_node(nid, ntype, label, health, risk=0, meta=None):
    if nid not in node_ids:
        node_ids.add(nid)
        graph_nodes.append({
            "id": nid,
            "type": ntype,
            "label": label,
            "health": health,
            "risk_score": risk,
            "meta": meta or {}
        })

# Add Warehouses
for wh in warehouses:
    add_node(wh["id"], "Warehouse", f"{wh['id']} ({wh['code']})", wh["health"], 85 if wh["id"] == "WH02" else 12, wh)

# Add Routes
for r in routes:
    add_node(r["id"], "Route", f"{r['id']} - {r['name'].split('/')[0]}", r["health"], 98 if r["id"] == "R05" else (20 if r["health"] == "HEALTHY" else 35), r)
    graph_edges.append({
        "id": f"e-{r['warehouse_id']}-{r['id']}",
        "source": r["warehouse_id"],
        "target": r["id"],
        "type": "ORIGINATES_FROM",
        "label": "Supplies Corridor"
    })

# Add Vehicles
for v in vehicles:
    add_node(v["id"], "Vehicle", f"{v['id']} ({v['driver'].split()[0]})", v["health"], 95 if v["id"] == "V23" else (15 if v["id"] != "V27" else 25), v)
    graph_edges.append({
        "id": f"e-{v['assigned_route']}-{v['id']}",
        "source": v["assigned_route"],
        "target": v["id"],
        "type": "TRANSITING_ON",
        "label": "Assigned Route"
    })

# Focus Deliveries for graph
featured_dids = ["D1045", "D1021", "D1022", "D1023", "D1024", "D1025", "D1026", "D1027", "D1028", "D1029", "D1030", 
                 "D1039", "D1040", "D1041", "D1067", "D1012", "D1015", "D1055", "D1072", "D1080"]

for did in featured_dids:
    d = next(item for item in deliveries if item["id"] == did)
    add_node(d["id"], "Delivery", f"{d['id']} ({d['title'][:16]}...)", d["health"], d["risk_score"], d)
    # Edge from Vehicle to Delivery
    graph_edges.append({
        "id": f"e-{d['vehicle_id']}-{d['id']}",
        "source": d["vehicle_id"],
        "target": d["id"],
        "type": "CARRIED_BY",
        "label": "Hauls Cargo"
    })
    # Add customer
    c = next(cust for cust in customers if cust["id"] == d["customer_id"])
    add_node(c["id"], "Customer", f"{c['id']} ({c['name'].split()[0]})", d["health"], d["risk_score"], c)
    # Edge from Delivery to Customer
    graph_edges.append({
        "id": f"e-{d['id']}-{c['id']}",
        "source": d["id"],
        "target": c["id"],
        "type": "DESTINED_FOR",
        "label": "Delivers To"
    })

# Alternate recovery path edge for AI visualization
graph_edges.append({
    "id": "e-rec-V27-D1045",
    "source": "V27",
    "target": "D1045",
    "type": "AI_PROPOSED_REDIRECT",
    "label": "Recovery Path (Feasibility 95%)",
    "dashed": True
})

output_data = {
    "warehouses": warehouses,
    "routes": routes,
    "vehicles": vehicles,
    "customers": customers,
    "deliveries": deliveries,
    "graph": {
        "nodes": graph_nodes,
        "edges": graph_edges
    },
    "kpis": {
        "active_deliveries": 1248,
        "deliveries_trend": "+4.2%",
        "vehicles_online": 87,
        "vehicles_total": 94,
        "at_risk_deliveries": 32,
        "at_risk_trend": "+8 from last hour",
        "active_disruptions": 3,
        "disruptions_severity": "1 Critical, 2 Moderate",
        "estimated_impact_usd": 18420,
        "impact_trend": "+$2,450 this hour",
        "recovery_success_rate": 94.7,
        "recovery_trend": "+1.3% vs 30-day baseline"
    }
}

with open("data/networkData.js", "w", encoding="utf-8") as f:
    f.write("// Logistics Resilience Network - Mock Data Source\n")
    f.write("window.LRN_DATA = " + json.dumps(output_data, indent=2) + ";\n")

print(f"Generated networkData.js successfully!")
print(f"Total Deliveries: {len(deliveries)}")
print(f"Total Vehicles: {len(vehicles)}")
print(f"Total Routes: {len(routes)}")
print(f"Total Customers: {len(customers)}")
print(f"Total Warehouses: {len(warehouses)}")
print(f"Graph Nodes: {len(graph_nodes)}, Edges: {len(graph_edges)}")
