"""
Logistics Resilience Network (LRN) - Backend Server
Supports zero-dependency standard library HTTP server + REST APIs
Integrated with production-structured AuthService, RBAC, and Server-Side Authorization
"""
import http.server
import socketserver
import json
import urllib.parse
import os
import sys

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

class LRNRequestHandler(http.server.SimpleHTTPRequestHandler):
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
        self.end_headers()

    def _extract_token(self) -> str:
        """Extracts Bearer token from Authorization header or URL query."""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:].strip()
        return ''

    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/health':
            self._send_json(200, {
                "status": "ONLINE",
                "system": "Logistics Resilience Network (LRN)",
                "graph_engine": "ACTIVE",
                "ai_engine": "ACTIVE",
                "auth_engine": "ACTIVE_RBAC",
                "lora_mesh": "LISTENING"
            })
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
            # Managers and admins can view audit logs
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
        # AUTHENTICATION ENDPOINTS
        # -------------------------------------------------------------
        if path == '/api/auth/login':
            user_id = payload.get('id', '')
            password = payload.get('password', '')
            role = payload.get('role', '')

            success, session_data, err_msg = auth_service.authenticate(user_id, password, role)
            if success and session_data:
                self._send_json(200, {
                    "success": True,
                    "message": f"Welcome, {session_data['display_name']}",
                    "token": session_data["token"],
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
        # PROTECTED LOGISTICS ACTIONS (SERVER-SIDE AUTHORIZATION ENFORCED)
        # -------------------------------------------------------------
        elif path == '/api/faults/report':
            # Role check: Employee or Operations Manager can report vehicle faults
            is_auth, session = auth_service.authorize(token, PERM_REPORT_VEHICLE_FAULTS)
            # Allow fallback for prototype if token is demo-verified
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
            # Server-side check: Disruption simulation requires manager/admin roles
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

            result = {
                "simulation_id": "SIM-" + str(os.urandom(3).hex().upper()),
                "status": "SIMULATED",
                "target": {"route": route, "vehicle": vehicle, "type": disruption_type, "severity": severity},
                "impact": {
                    "direct_deliveries": 18 if route == 'R05' else 8,
                    "secondary_deliveries": 27 if route == 'R05' else 14,
                    "potential_sla_breaches": 7 if severity == 'CRITICAL' else 3,
                    "affected_vehicles": 4 if route == 'R05' else 2,
                    "estimated_cost_usd": 2450 if severity == 'CRITICAL' else 980,
                    "risk_level": "HIGH" if severity == 'CRITICAL' else "MEDIUM"
                },
                "ripple_nodes": ["R05", "V23", "D1045", "D1021", "D1022", "D1023", "C208"]
            }
            self._send_json(200, result)
            return

        elif path == '/api/recoveries/apply':
            # Server-side check: Operations Manager can apply; Logistics Manager can approve
            is_ops, session = auth_service.authorize(token, PERM_APPLY_RECOVERY_ACTIONS)
            is_mgr, _ = auth_service.authorize(token, PERM_APPROVE_RECOVERY_ACTIONS)

            if not (is_ops or is_mgr):
                self._send_json(403, {
                    "error": "Access Denied: Only Operations and Logistics Managers can commit recovery actions."
                })
                return

            plan_id = payload.get('plan_id', 'LRN-2048')
            strategy = payload.get('strategy', 'REDIRECT')
            action_type = "APPLIED" if is_ops else "APPROVED"

            auth_service.log_audit("RECOVERY_COMMITTED", session.get('user_id'), session.get('role'), action_type, f"Plan {plan_id} ({strategy}) committed")

            self._send_json(200, {
                "status": action_type,
                "plan_id": plan_id,
                "strategy": strategy,
                "authorized_by": f"{session.get('display_name')} ({session.get('role')})",
                "assigned_vehicle": "V27",
                "new_eta": "15:18",
                "sla_secured": True,
                "message": f"Recovery plan successfully {action_type.lower()} by {session.get('role')}."
            })
            return

        elif path == '/api/sos/transmit':
            # Employee and Managers can transmit SOS
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
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), LRNRequestHandler) as httpd:
        print(f"================================================================")
        print(f"Logistics Resilience Network (LRN) Command Center Server")
        print(f"Security: RBAC & Salted PBKDF2 Password Authentication Enabled")
        print(f"LRN Command System available at: http://localhost:{PORT}")
        print(f"Serving files from: {BASE_DIR}")
        print(f"================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == '__main__':
    run_server()
