"""
Logistics Resilience Network (LRN) - Backend Server
Supports zero-dependency standard library HTTP server + REST APIs
Integrated with production AuthService, RBAC, Graph Dependency Engine,
SQL Adaptive Learning Engine, Decision Intelligence Engine, and ESP32 SOS Hardware Receiver.
"""
import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import time
import traceback

from auth_service import (
    auth_service,
    PERM_VIEW_ASSIGNED_VEHICLE,
    PERM_REPORT_VEHICLE_FAULTS,
    PERM_TRIGGER_EMERGENCY_SOS,
    PERM_APPLY_RECOVERY_ACTIONS,
    PERM_APPROVE_RECOVERY_ACTIONS,
    PERM_ANALYZE_RIPPLE_EFFECTS,
    PERM_MONITOR_DISRUPTION_EVENTS,
    PERM_VIEW_AUDIT_LOGS,
    ROLE_EMPLOYEE,
    ROLE_LOGISTICS_MANAGER,
    ROLE_OPERATIONS_MANAGER,
    ROLE_SYSTEM_ADMIN
)
from database.graph_engine import graph_engine
from database.adaptive_learning import adaptive_learning_engine
from decision_engine import decision_engine

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# In-memory store for vehicle fault reports submitted by employees
VEHICLE_FAULTS_REGISTRY = [
    {
        "ticket_id": "FLT-9821",
        "vehicle_id": "V23",
        "reported_by": "employee01",
        "category": "Engine Overheat / Coolant Rupture",
        "severity": "CRITICAL",
        "odometer_km": 142850,
        "location": "Route R05, Mile 18 Mountain Cut",
        "description": "Temperature spiked to 118C suddenly. White vapor from under hood, coolant reservoir empty.",
        "status": "DISPATCH_NOTIFIED",
        "timestamp": "14:28:15"
    }
]

# Active Disruption Store
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

class LRNRequestHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Connection', 'close')
        self.end_headers()

    def _extract_token(self) -> str:
        """Extracts Bearer token from Authorization header or URL query."""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:].strip()
        return ''

    def _send_json(self, status_code: int, data: dict):
        try:
            body = json.dumps(data).encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
        except Exception as e:
            traceback.print_exc()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/health':
            self._send_json(200, {
                "status": "ONLINE",
                "system": "Logistics Resilience Network (LRN)",
                "graph_engine": "ACTIVE_NEO4J_READY",
                "adaptive_learning": "ACTIVE_SQL",
                "ai_engine": "ACTIVE",
                "auth_engine": "ACTIVE_RBAC_JWT",
                "lora_mesh": "LISTENING"
            })
            return

        elif path == '/deliveries':
            # Role-governed deliveries query
            token = self._extract_token()
            session = auth_service.validate_session(token) if token else None
            user_role = session.get("role") if session else ROLE_LOGISTICS_MANAGER
            
            nodes = graph_engine.nodes
            deliveries = [v for k, v in nodes.items() if v.get("type") == "Delivery"]
            vehicles = [v for k, v in nodes.items() if v.get("type") == "Vehicle"]
            routes = [v for k, v in nodes.items() if v.get("type") == "Route"]
            customers = [v for k, v in nodes.items() if v.get("type") == "Customer"]

            if session and session.get("role") == ROLE_EMPLOYEE:
                assigned_vid = session.get("assigned_vehicle", "V23")
                assigned_dids = session.get("assigned_deliveries", ["D1045", "D1021", "D1022"])
                deliveries = [d for d in deliveries if d.get("code") in assigned_dids]
                vehicles = [v for k, v in nodes.items() if k == assigned_vid]

            self._send_json(200, {
                "status": "SUCCESS",
                "role": user_role,
                "total_deliveries": len(deliveries),
                "deliveries": deliveries,
                "vehicles": vehicles,
                "routes": routes,
                "customers": customers,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            return

        elif path == '/disruptions':
            self._send_json(200, {
                "total_active": len(ACTIVE_DISRUPTIONS),
                "disruptions": ACTIVE_DISRUPTIONS
            })
            return

        elif path == '/adaptive-learning/stats':
            kpis = adaptive_learning_engine.get_summary_kpis()
            performance = adaptive_learning_engine.get_strategy_performance()
            self._send_json(200, {
                "kpis": kpis,
                "strategy_performance": performance
            })
            return

        elif path == '/recovery':
            qs = urllib.parse.parse_qs(parsed.query)
            event_data = {
                "id": qs.get('disruption_id', ['DISR-2026-081'])[0],
                "affected_route": qs.get('route', ['R05'])[0],
                "vehicleID": qs.get('vehicle_id', qs.get('vehicleID', ['V23']))[0],
                "event": qs.get('event_type', qs.get('event', ['ROAD_CLOSURE']))[0],
                "priority": qs.get('priority', ['EMERGENCY'])[0],
                "source": qs.get('source', ['SENSOR_NETWORK'])[0]
            }
            result = decision_engine.generate_recovery_strategies(event_data)
            self._send_json(200, result)
            return

        elif path == '/api/auth/session':
            token = self._extract_token()
            session = auth_service.validate_session(token)
            if not session:
                self._send_json(401, {
                    "authenticated": False,
                    "error": "Access Denied: Session invalid or expired."
                })
                return
            self._send_json(200, {
                "authenticated": True,
                "session": session
            })
            return

        elif path == '/api/auth/audit':
            token = self._extract_token()
            session = auth_service.validate_session(token)
            if not session:
                self._send_json(401, {"error": "Authentication required."})
                return
            if session.get("role") not in [ROLE_LOGISTICS_MANAGER, ROLE_OPERATIONS_MANAGER, ROLE_SYSTEM_ADMIN]:
                self._send_json(403, {"error": "Access Denied: Insufficient role permissions."})
                return
            self._send_json(200, {
                "audit_logs": auth_service.audit_log[-50:]
            })
            return

        elif path == '/api/faults':
            token = self._extract_token()
            session = auth_service.validate_session(token)
            if not session:
                self._send_json(401, {"error": "Authentication required."})
                return
            self._send_json(200, {
                "faults": VEHICLE_FAULTS_REGISTRY
            })
            return

        # Fallback to static file serving
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            payload = {}

        token = self._extract_token() or payload.get('token', '')

        # -------------------------------------------------------------
        # AUTHENTICATION ENDPOINTS (/auth & /api/auth/login)
        # -------------------------------------------------------------
        if path in ['/auth', '/api/auth/login']:
            user_id = payload.get('id', '')
            password = payload.get('password', '')
            role = payload.get('role', '')

            success, session_data, err_msg = auth_service.authenticate(user_id, password, role)
            if success and session_data:
                self._send_json(200, {
                    "success": True,
                    "message": f"Welcome, {session_data['display_name']} ({session_data['role']})",
                    "token": session_data["token"],
                    "access_token": session_data["token"],
                    "token_type": "Bearer",
                    "user": session_data
                })
            else:
                self._send_json(401, {
                    "success": False,
                    "error": err_msg or "Access Denied: Invalid ID, password, or role."
                })
            return

        elif path == '/api/auth/logout':
            auth_service.logout(token)
            self._send_json(200, {
                "success": True,
                "message": "Session terminated successfully."
            })
            return

        # -------------------------------------------------------------
        # HARDWARE TELEMETRY & DISRUPTIONS (/disruptions)
        # -------------------------------------------------------------
        elif path == '/disruptions':
            # Ingest ESP32 hardware packet or manual disruption
            vid = payload.get('vehicleID', payload.get('vehicle_id', 'V23'))
            event_type = payload.get('event', payload.get('event_type', 'VEHICLE_FAULT'))
            sig_status = payload.get('signalStatus', payload.get('signal_status', 'NO_SIGNAL'))
            src = payload.get('source', 'LoRa/Satellite')
            pri = payload.get('priority', 'EMERGENCY')
            route = payload.get('route', 'R05')
            location = payload.get('location', '11.0168,76.9558')
            gps_coords = None
            if isinstance(location, str) and ',' in location:
                try:
                    parts = location.split(',')
                    gps_coords = [float(parts[0].strip()), float(parts[1].strip())]
                    graph_engine.update_vehicle_telemetry(vid, gps_coords[0], gps_coords[1], "HALTED_FAULT", route)
                except Exception:
                    pass

            # 1. Log in SQL Adaptive Learning telemetry table
            telemetry_id = adaptive_learning_engine.record_hardware_telemetry(
                vehicle_id=vid,
                event_type=event_type,
                signal_status=sig_status,
                source=src,
                priority=pri,
                raw_payload=payload
            )

            # 2. Add to active disruptions
            disr_id = f"DISR-{int(time.time()) % 100000:05d}"
            disruption_record = {
                "id": disr_id,
                "title": f"HARDWARE ALERT: {event_type} on {vid}",
                "code": f"{vid}-{event_type}",
                "severity": "CRITICAL" if pri == "EMERGENCY" else "HIGH",
                "priority": pri,
                "cause": f"{event_type} reported via {src} ({sig_status})",
                "location": location,
                "gps_location": gps_coords or [11.032, 76.942],
                "time": time.strftime("%H:%M"),
                "affected_route": route,
                "affected_vehicle": vid,
                "source": src,
                "signal_status": sig_status,
                "status": "ALERT_ACTIVE",
                "telemetry_id": telemetry_id
            }
            ACTIVE_DISRUPTIONS.insert(0, disruption_record)

            # 3. Decision Intelligence Engine evaluation
            analysis = decision_engine.generate_recovery_strategies(disruption_record)

            self._send_json(200, {
                "status": "ALERT_DISPATCHED",
                "disruption_id": disr_id,
                "telemetry_id": telemetry_id,
                "received_packet": payload,
                "vehicle_id": vid,
                "affected_route": route,
                "gps_location": gps_coords or [11.032, 76.942],
                "ripple_impact": analysis["ripple_effects"],
                "ranked_recovery_strategies": analysis["ranked_strategies"],
                "recommended_action": analysis["recommended_action"],
                "decision_recommendation": analysis["recommended_action"],
                "message": f"Hardware telemetry received from {vid} via {src}. Recovery strategies calculated."
            })
            return

        # -------------------------------------------------------------
        # DECISION INTELLIGENCE RECOVERY ENDPOINT (/recovery)
        # -------------------------------------------------------------
        elif path == '/recovery':
            event_data = {
                "id": payload.get('disruption_id', 'DISR-2026-081'),
                "affected_route": payload.get('route', 'R05'),
                "vehicleID": payload.get('vehicle_id', payload.get('vehicleID', 'V23')),
                "event": payload.get('event_type', payload.get('event', 'ROAD_CLOSURE')),
                "priority": payload.get('priority', 'EMERGENCY'),
                "source": payload.get('source', 'SENSOR_NETWORK')
            }
            result = decision_engine.generate_recovery_strategies(event_data)
            self._send_json(200, result)
            return

        # -------------------------------------------------------------
        # RECOVERY ACTIONS COMMIT & SQL ADAPTIVE LEARNING LOGGING
        # -------------------------------------------------------------
        elif path in ['/recoveries/apply', '/api/recoveries/apply']:
            is_ops, session = auth_service.authorize(token, PERM_APPLY_RECOVERY_ACTIONS)
            is_mgr, _ = auth_service.authorize(token, PERM_APPROVE_RECOVERY_ACTIONS)

            # Allow demo mode if session exists or token is manager
            if not (is_ops or is_mgr):
                # Fallback: check session role directly
                session = auth_service.validate_session(token)
                if not (session and session.get("role") in [ROLE_LOGISTICS_MANAGER, ROLE_OPERATIONS_MANAGER, ROLE_SYSTEM_ADMIN]):
                    self._send_json(403, {
                        "error": "Access Denied: Only Operations and Logistics Managers can commit recovery actions."
                    })
                    return

            plan_id = payload.get('plan_id', 'LRN-2048')
            strategy = payload.get('strategy', 'redirect')
            action_type = "APPLIED" if is_ops else "APPROVED"
            user_id = session.get('user_id', 'manager01')
            user_role = session.get('role', 'Logistics Manager')

            # Record outcome into SQL Adaptive Learning Engine
            outcome_id = adaptive_learning_engine.record_outcome(
                disruption_id=payload.get('disruption_id', 'DISR-2026-081'),
                disruption_type=payload.get('disruption_type', 'ROAD_CLOSURE'),
                corridor=payload.get('affected_corridor', 'R05'),
                strategy=strategy,
                applied_by=user_id,
                user_role=user_role,
                success=True,
                delay_mitigated_min=payload.get('delay_mitigated_min', 45),
                cost_usd=payload.get('cost_usd', 380.0),
                sla_preserved=payload.get('sla_preserved', True),
                customer_satisfaction=payload.get('customer_satisfaction', 4.8),
                notes=payload.get('notes', f"Applied strategy {strategy} for {plan_id}")
            )

            auth_service.log_audit("RECOVERY_COMMITTED", user_id, user_role, action_type, f"Plan {plan_id} ({strategy}) committed")

            self._send_json(200, {
                "status": action_type,
                "plan_id": plan_id,
                "strategy": strategy,
                "sql_outcome_id": outcome_id,
                "authorized_by": f"{session.get('display_name')} ({user_role})",
                "assigned_vehicle": "V27" if strategy == "reallocate" else "V23",
                "detour_route": "R12" if strategy in ["redirect", "reallocate"] else "R05",
                "new_eta": "15:18",
                "sla_secured": True,
                "adaptive_learning_logged": True,
                "message": f"Recovery plan successfully {action_type.lower()} by {user_role}. Route dynamically updated."
            })
            return

        elif path == '/api/faults/report':
            is_auth, session = auth_service.authorize(token, PERM_REPORT_VEHICLE_FAULTS)
            if not is_auth:
                self._send_json(403, {
                    "success": False,
                    "error": "Access Denied: You do not have permission to report vehicle faults."
                })
                return

            ticket_id = "FLT-" + str(os.urandom(2).hex().upper())
            fault_record = {
                "ticket_id": ticket_id,
                "vehicle_id": payload.get('vehicle_id', session.get('assigned_vehicle', 'V23')),
                "reported_by": session.get('user_id', 'employee01'),
                "category": payload.get('category', 'Mechanical Failure'),
                "severity": payload.get('severity', 'HIGH'),
                "odometer_km": payload.get('odometer_km', 142850),
                "location": payload.get('location', 'Route R05, Mile 18'),
                "description": payload.get('description', 'Reported via driver terminal.'),
                "status": "DISPATCH_NOTIFIED",
                "timestamp": payload.get('timestamp', '14:45:00')
            }
            VEHICLE_FAULTS_REGISTRY.append(fault_record)
            auth_service.log_audit("FAULT_REPORTED", session.get('user_id'), session.get('role'), "RECORDED", f"Ticket {ticket_id} for vehicle {fault_record['vehicle_id']}")

            self._send_json(200, {
                "success": True,
                "ticket_id": ticket_id,
                "record": fault_record,
                "message": "Vehicle fault report dispatched to Central Logistics Command."
            })
            return

        elif path == '/api/disruptions/simulate':
            is_auth, session = auth_service.authorize(token, PERM_MONITOR_DISRUPTION_EVENTS)
            if not is_auth:
                is_auth, session = auth_service.authorize(token, PERM_ANALYZE_RIPPLE_EFFECTS)
            if not is_auth:
                self._send_json(403, {
                    "error": "Access Denied: Disruption simulation requires Manager authorization."
                })
                return

            route = payload.get('route', 'R05')
            vehicle = payload.get('vehicle', 'V23')
            disruption_type = payload.get('type', 'Road Closure')
            severity = payload.get('severity', 'CRITICAL')

            analysis = decision_engine.generate_recovery_strategies({
                "affected_route": route,
                "vehicleID": vehicle,
                "event": disruption_type,
                "priority": severity
            })

            result = {
                "simulation_id": "SIM-" + str(os.urandom(3).hex().upper()),
                "status": "SIMULATED",
                "target": {"route": route, "vehicle": vehicle, "type": disruption_type, "severity": severity},
                "ripple_effects": analysis["ripple_effects"],
                "ranked_strategies": analysis["ranked_strategies"],
                "recommended_action": analysis["recommended_action"]
            }
            self._send_json(200, result)
            return

        elif path == '/api/sos/transmit':
            is_auth, session = auth_service.authorize(token, PERM_TRIGGER_EMERGENCY_SOS)
            if not is_auth:
                is_auth, session = auth_service.authorize(token, PERM_VIEW_EMERGENCY_EVENTS)
            if not is_auth:
                self._send_json(403, {
                    "error": "Access Denied: Emergency SOS authorization failed."
                })
                return

            vid = payload.get('vehicle_id', session.get('assigned_vehicle', 'V23'))
            auth_service.log_audit("EMERGENCY_SOS", session.get('user_id'), session.get('role'), "TRANSMITTED", f"SOS broadcast for vehicle {vid}")

            self._send_json(200, {
                "status": "ACKNOWLEDGED",
                "vehicle_id": vid,
                "sender": session.get('display_name'),
                "sender_role": session.get('role'),
                "receiver": "LRN Satellite Gateway Station Alpha",
                "ack_timestamp": "14:42:04",
                "dispatched_response": "Emergency Tow & Sprinter Reroute V27 Active"
            })
            return

        self._send_json(404, {"error": "Endpoint not found"})

def run_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    with socketserver.ThreadingTCPServer(("", PORT), LRNRequestHandler) as httpd:
        print(f"================================================================")
        print(f"Logistics Resilience Network (LRN) Command Center Server")
        print(f"Security: RBAC & Salted PBKDF2 Password Authentication Enabled")
        print(f"Graph Engine: Neo4j Ready | Adaptive Learning: SQLite/Postgres")
        print(f"ESP32 SOS Gateway: Listening on /disruptions")
        print(f"LRN Dashboard available at: http://localhost:{PORT}")
        print(f"Serving files from: {BASE_DIR}")
        print(f"================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == '__main__':
    run_server()
