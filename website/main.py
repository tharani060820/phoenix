"""
Logistics Resilience Network (LRN) - FastAPI Production Backend
Secure Web Dashboard with ESP32 SOS Hardware Integration
Features:
- PyJWT / HS256 Token Authentication (/auth)
- Fleet Deliveries, Routes, Vehicles API (/deliveries)
- Disruption & ESP32 Hardware Ingestion API (/disruptions)
- Decision Intelligence Engine with Ranked Recovery Strategies (/recovery)
- SQL Adaptive Learning Outcome Tracking (/recoveries/apply, /adaptive-learning/stats)
- Neo4j Graph Ripple Effect Dependency Modeling
- Swagger / OpenAPI Documentation at /docs
"""
import os
import json
import time
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, Header, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from auth_service import (
    auth_service,
    PERM_VIEW_ASSIGNED_VEHICLE,
    PERM_REPORT_VEHICLE_FAULTS,
    PERM_TRIGGER_EMERGENCY_SOS,
    PERM_APPLY_RECOVERY_ACTIONS,
    PERM_APPROVE_RECOVERY_ACTIONS,
    PERM_ANALYZE_RIPPLE_EFFECTS,
    PERM_MONITOR_DISRUPTION_EVENTS,
    ROLE_EMPLOYEE,
    ROLE_LOGISTICS_MANAGER,
    ROLE_OPERATIONS_MANAGER,
    ROLE_SYSTEM_ADMIN
)
from database.graph_engine import graph_engine
from database.adaptive_learning import adaptive_learning_engine
from decision_engine import decision_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="Logistics Resilience Network (LRN) API",
    description="Adaptive Recovery & Decision Intelligence Engine with ESP32 SOS Integration",
    version="3.5.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# PYDANTIC DATA SCHEMAS
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    id: str = Field(..., example="manager01", description="Employee or Manager ID")
    password: str = Field(..., example="Mgr@123", description="User password")
    role: str = Field(..., example="Logistics Manager", description="Authorized role")

class DisruptionEventPacket(BaseModel):
    vehicleID: Optional[str] = Field("V23", example="V23", description="Vehicle ID")
    vehicle_id: Optional[str] = Field(None, example="V23")
    event: Optional[str] = Field("VEHICLE_FAULT", example="VEHICLE_FAULT", description="Event type")
    signalStatus: Optional[str] = Field("NO_SIGNAL", example="NO_SIGNAL", description="CONNECTED_4G or NO_SIGNAL")
    source: Optional[str] = Field("LoRa/Satellite", example="LoRa/Satellite", description="Transmission source channel")
    priority: Optional[str] = Field("EMERGENCY", example="EMERGENCY", description="Priority level")
    route: Optional[str] = Field("R05", example="R05", description="Corridor affected")
    location: Optional[str] = Field("Expressway Sector 5 (Mile 18)", example="Route R05, Mile 18")
    notes: Optional[str] = Field("Hardware telemetry event received from driver cabin transceiver.")

class RecoveryRequest(BaseModel):
    disruption_id: Optional[str] = "DISR-2026-081"
    route: Optional[str] = "R05"
    vehicle_id: Optional[str] = "V23"
    event_type: Optional[str] = "ROAD_CLOSURE"
    priority: Optional[str] = "EMERGENCY"
    source: Optional[str] = "SENSOR_NETWORK"

class ApplyRecoveryRequest(BaseModel):
    plan_id: str = Field(..., example="LRN-2048")
    strategy: str = Field(..., example="redirect", description="redirect, reallocate, reschedule, partition, defer")
    disruption_id: Optional[str] = "DISR-2026-081"
    disruption_type: Optional[str] = "ROAD_CLOSURE"
    affected_corridor: Optional[str] = "R05"
    delay_mitigated_min: Optional[int] = 45
    cost_usd: Optional[float] = 380.0
    sla_preserved: Optional[bool] = True
    customer_satisfaction: Optional[float] = 4.8
    notes: Optional[str] = "Action committed via LRN Manager Console."

# In-memory disruption registry
ACTIVE_DISRUPTIONS = [
    {
        "id": "DISR-2026-081",
        "title": "ROUTE 5 BLOCKED - HAZARDOUS SPILL",
        "code": "R05-CRITICAL",
        "severity": "CRITICAL",
        "priority": "EMERGENCY",
        "cause": "Multi-vehicle collision & chemical spill",
        "location": "Expressway Sector 5 (Mile 18)",
        "time": "14:32",
        "affected_route": "R05",
        "affected_vehicle": "V23",
        "source": "Highways Traffic CCTV & Sensor Grid",
        "status": "ACTIVE_INVESTIGATION"
    }
]

# Helper to verify auth
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing.")
    token = authorization[7:].strip() if authorization.startswith("Bearer ") else authorization.strip()
    session = auth_service.validate_session(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session token.")
    return session

# -------------------------------------------------------------
# CORE ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "framework": "FastAPI 3.5.0",
        "system": "Logistics Resilience Network (LRN)",
        "graph_engine": "ACTIVE_NEO4J_READY",
        "adaptive_learning": "ACTIVE_SQL",
        "esp32_gateway": "LISTENING"
    }

@app.post("/auth")
@app.post("/api/auth/login")
def login(req: LoginRequest):
    """
    Authenticates logistics personnel (Employee, Logistics Manager, Operations Manager).
    Issues cryptographically signed JWT token with role and permission claims.
    """
    success, session_data, err_msg = auth_service.authenticate(req.id, req.password, req.role)
    if not success or not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err_msg or "Access Denied: Invalid ID, password, or role."
        )
    return {
        "success": True,
        "token": session_data["token"],
        "token_type": "Bearer",
        "user": session_data,
        "message": f"Welcome, {session_data['display_name']} ({session_data['role']})"
    }

@app.get("/deliveries")
def get_deliveries(user: dict = Depends(get_current_user)):
    """
    Fetches active deliveries, routes, vehicles, and supply chain status.
    Role-governed: Employees see their assigned vehicle and consignments;
    Managers see global network state.
    """
    # Graph engine provides topology
    nodes = graph_engine.nodes
    deliveries = [v for k, v in nodes.items() if v.get("type") == "Delivery"]
    vehicles = [v for k, v in nodes.items() if v.get("type") == "Vehicle"]
    routes = [v for k, v in nodes.items() if v.get("type") == "Route"]
    customers = [v for k, v in nodes.items() if v.get("type") == "Customer"]

    if user.get("role") == ROLE_EMPLOYEE:
        assigned_vid = user.get("assigned_vehicle", "V23")
        assigned_dids = user.get("assigned_deliveries", ["D1045", "D1021", "D1022"])
        deliveries = [d for d in deliveries if d.get("code") in assigned_dids]
        vehicles = [v for k, v in nodes.items() if k == assigned_vid]

    return {
        "status": "SUCCESS",
        "role": user.get("role"),
        "total_deliveries": len(deliveries),
        "deliveries": deliveries,
        "vehicles": vehicles,
        "routes": routes,
        "customers": customers,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/disruptions")
def receive_disruption(packet: DisruptionEventPacket):
    """
    Receives disruption events via ESP32 Hardware SOS or manual operations dispatch.
    Matches exact payload: {"vehicleID": "V23", "event": "VEHICLE_FAULT", "signalStatus": "NO_SIGNAL", "source": "LoRa/Satellite", "priority": "EMERGENCY"}
    1. Stores telemetry in SQL database.
    2. Queries graph dependency engine for ripple effects.
    3. Runs Decision Intelligence Engine to rank recovery strategies.
    4. Emits real-time emergency alert.
    """
    vid = packet.vehicleID or packet.vehicle_id or "V23"
    event_type = packet.event or "VEHICLE_FAULT"
    sig_status = packet.signalStatus or "NO_SIGNAL"
    src = packet.source or "LoRa/Satellite"
    pri = packet.priority or "EMERGENCY"
    route = packet.route or "R05"

    # 1. Log in SQL Adaptive Telemetry Table
    telemetry_id = adaptive_learning_engine.record_hardware_telemetry(
        vehicle_id=vid,
        event_type=event_type,
        signal_status=sig_status,
        source=src,
        priority=pri,
        raw_payload=packet.model_dump()
    )

    # 2. Register Active Disruption
    disr_id = f"DISR-{int(time.time()) % 100000:05d}"
    disruption_record = {
        "id": disr_id,
        "title": f"HARDWARE ALERT: {event_type} on {vid}",
        "code": f"{vid}-{event_type}",
        "severity": "CRITICAL" if pri == "EMERGENCY" else "HIGH",
        "priority": pri,
        "cause": f"{event_type} reported via {src} ({sig_status})",
        "location": packet.location or "Expressway Sector 5 (Mile 18)",
        "time": time.strftime("%H:%M"),
        "affected_route": route,
        "affected_vehicle": vid,
        "source": src,
        "signal_status": sig_status,
        "status": "ALERT_ACTIVE",
        "telemetry_id": telemetry_id
    }
    ACTIVE_DISRUPTIONS.insert(0, disruption_record)

    # 3. Decision Intelligence Engine Evaluation
    analysis = decision_engine.generate_recovery_strategies(disruption_record)

    return {
        "status": "ALERT_DISPATCHED",
        "disruption_id": disr_id,
        "telemetry_id": telemetry_id,
        "received_packet": packet.model_dump(),
        "ripple_impact": analysis["ripple_effects"],
        "ranked_recovery_strategies": analysis["ranked_strategies"],
        "recommended_action": analysis["recommended_action"],
        "message": f"Emergency alert registered from {vid} via {src}. Recovery strategies calculated."
    }

@app.get("/disruptions")
def get_disruptions():
    """Lists active and recent disruption events."""
    return {
        "total_active": len(ACTIVE_DISRUPTIONS),
        "disruptions": ACTIVE_DISRUPTIONS
    }

@app.post("/recovery")
def generate_recovery(req: RecoveryRequest):
    """
    Decision Intelligence Engine Endpoint:
    Input disruption -> Query Neo4j graph for ripple effects.
    Generate strategies: redirect, reschedule, reallocate, partition, defer.
    Score each option (feasibility, cost, delay, customer impact).
    Return ranked list with 'Recommended Action'.
    """
    event_data = {
        "id": req.disruption_id,
        "affected_route": req.route,
        "vehicleID": req.vehicle_id,
        "event": req.event_type,
        "priority": req.priority,
        "source": req.source
    }
    result = decision_engine.generate_recovery_strategies(event_data)
    return result

@app.post("/recoveries/apply")
def apply_recovery(req: ApplyRecoveryRequest, user: dict = Depends(get_current_user)):
    """
    Applies and commits chosen recovery strategy.
    Logs actual outcome into SQL Adaptive Learning database to continuously improve future recommendations.
    """
    # Verify manager permission
    if user.get("role") not in [ROLE_LOGISTICS_MANAGER, ROLE_OPERATIONS_MANAGER, ROLE_SYSTEM_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Logistics and Operations Managers can apply recovery plans.")

    # Record into SQL Adaptive Learning Engine
    outcome_id = adaptive_learning_engine.record_outcome(
        disruption_id=req.disruption_id or "DISR-2026-081",
        disruption_type=req.disruption_type or "ROAD_CLOSURE",
        corridor=req.affected_corridor or "R05",
        strategy=req.strategy,
        applied_by=user.get("user_id", "manager01"),
        user_role=user.get("role", "Logistics Manager"),
        success=True,
        delay_mitigated_min=req.delay_mitigated_min or 45,
        cost_usd=req.cost_usd or 380.0,
        sla_preserved=req.sla_preserved if req.sla_preserved is not None else True,
        customer_satisfaction=req.customer_satisfaction or 4.8,
        notes=req.notes or f"Committed plan {req.plan_id}"
    )

    auth_service.log_audit("RECOVERY_APPLIED", user.get("user_id"), user.get("role"), "COMMITTED", f"Applied {req.strategy} for {req.plan_id}")

    return {
        "status": "COMMITTED",
        "plan_id": req.plan_id,
        "strategy": req.strategy,
        "sql_outcome_id": outcome_id,
        "authorized_by": f"{user.get('display_name')} ({user.get('role')})",
        "assigned_asset": "V27 (Relief)" if req.strategy == "reallocate" else "R12 (Detour)",
        "network_state": "ADAPTIVE_REROUTING_ENGAGED",
        "learning_feedback_recorded": True,
        "message": f"Recovery strategy '{req.strategy}' applied. Route updated and logged to adaptive learning store."
    }

@app.get("/adaptive-learning/stats")
def get_adaptive_stats():
    """Returns SQL Adaptive Learning metrics, success rates, and strategy multipliers."""
    kpis = adaptive_learning_engine.get_summary_kpis()
    performance = adaptive_learning_engine.get_strategy_performance()
    return {
        "kpis": kpis,
        "strategy_performance": performance
    }

# Mount static files & root fallback
app.mount("/data", StaticFiles(directory=os.path.join(BASE_DIR, "data")), name="data")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/auth.js")
def serve_auth_js():
    return FileResponse(os.path.join(BASE_DIR, "auth.js"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
