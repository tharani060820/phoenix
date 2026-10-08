"""
Logistics Resilience Network (LRN) - Authentication & RBAC Service
Production-grade security module providing:
- Salted password hashing (PBKDF2-HMAC-SHA256 with 100,000 iterations; drop-in hooks for bcrypt/argon2)
- Cryptographic session token generation & lifecycle management
- Role-Based Access Control (RBAC) matrix
- Server-side authorization verification
- Security audit event logging
"""

import hashlib
import os
import secrets
import time
from typing import Dict, List, Optional, Tuple, Any

# ==============================================================================
# 1. PERMISSIONS & ROLES DEFINITIONS (RBAC MATRIX)
# ==============================================================================

# Permission constants
PERM_VIEW_ASSIGNED_VEHICLE = "view_assigned_vehicle"
PERM_VIEW_ASSIGNED_DELIVERY = "view_assigned_delivery"
PERM_REPORT_VEHICLE_FAULTS = "report_vehicle_faults"
PERM_TRIGGER_EMERGENCY_SOS = "trigger_emergency_sos"
PERM_VIEW_RECOVERY_INSTRUCTIONS = "view_recovery_instructions"

PERM_VIEW_VEHICLES = "view_vehicles"
PERM_VIEW_ROUTES = "view_routes"
PERM_VIEW_DELIVERIES = "view_deliveries"
PERM_VIEW_DISRUPTIONS = "view_disruptions"
PERM_ANALYZE_RIPPLE_EFFECTS = "analyze_ripple_effects"
PERM_VIEW_RECOVERY_STRATEGIES = "view_recovery_strategies"
PERM_APPROVE_RECOVERY_ACTIONS = "approve_recovery_actions"
PERM_VIEW_EMERGENCY_EVENTS = "view_emergency_events"

PERM_MANAGE_VEHICLES = "manage_vehicles"
PERM_MANAGE_ROUTES = "manage_routes"
PERM_MANAGE_DELIVERIES = "manage_deliveries"
PERM_APPLY_RECOVERY_ACTIONS = "apply_recovery_actions"
PERM_MONITOR_DISRUPTION_EVENTS = "monitor_disruption_events"
PERM_MANAGE_OPERATIONAL_INFO = "manage_operational_info"

# System Administrator extensions
PERM_MANAGE_USERS = "manage_users"
PERM_MANAGE_SYSTEM = "manage_system"
PERM_VIEW_AUDIT_LOGS = "view_audit_logs"

# Role Names
ROLE_EMPLOYEE = "Employee"
ROLE_LOGISTICS_MANAGER = "Logistics Manager"
ROLE_OPERATIONS_MANAGER = "Operations Manager"
ROLE_SYSTEM_ADMIN = "System Administrator"

# Role Permission Mapping
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    ROLE_EMPLOYEE: [
        PERM_VIEW_ASSIGNED_VEHICLE,
        PERM_VIEW_ASSIGNED_DELIVERY,
        PERM_REPORT_VEHICLE_FAULTS,
        PERM_TRIGGER_EMERGENCY_SOS,
        PERM_VIEW_RECOVERY_INSTRUCTIONS,
    ],
    ROLE_LOGISTICS_MANAGER: [
        PERM_VIEW_VEHICLES,
        PERM_VIEW_ROUTES,
        PERM_VIEW_DELIVERIES,
        PERM_VIEW_DISRUPTIONS,
        PERM_ANALYZE_RIPPLE_EFFECTS,
        PERM_VIEW_RECOVERY_STRATEGIES,
        PERM_APPROVE_RECOVERY_ACTIONS,
        PERM_VIEW_EMERGENCY_EVENTS,
        PERM_VIEW_ASSIGNED_VEHICLE,
        PERM_VIEW_ASSIGNED_DELIVERY,
    ],
    ROLE_OPERATIONS_MANAGER: [
        PERM_MANAGE_VEHICLES,
        PERM_MANAGE_ROUTES,
        PERM_MANAGE_DELIVERIES,
        PERM_APPLY_RECOVERY_ACTIONS,
        PERM_MONITOR_DISRUPTION_EVENTS,
        PERM_MANAGE_OPERATIONAL_INFO,
        PERM_VIEW_VEHICLES,
        PERM_VIEW_ROUTES,
        PERM_VIEW_DELIVERIES,
        PERM_VIEW_DISRUPTIONS,
        PERM_ANALYZE_RIPPLE_EFFECTS,
        PERM_VIEW_RECOVERY_STRATEGIES,
        PERM_VIEW_EMERGENCY_EVENTS,
    ],
    ROLE_SYSTEM_ADMIN: [
        # Full administrative rights for system expansion
        PERM_VIEW_VEHICLES, PERM_VIEW_ROUTES, PERM_VIEW_DELIVERIES, PERM_VIEW_DISRUPTIONS,
        PERM_ANALYZE_RIPPLE_EFFECTS, PERM_VIEW_RECOVERY_STRATEGIES, PERM_APPROVE_RECOVERY_ACTIONS,
        PERM_VIEW_EMERGENCY_EVENTS, PERM_MANAGE_VEHICLES, PERM_MANAGE_ROUTES, PERM_MANAGE_DELIVERIES,
        PERM_APPLY_RECOVERY_ACTIONS, PERM_MONITOR_DISRUPTION_EVENTS, PERM_MANAGE_OPERATIONAL_INFO,
        PERM_REPORT_VEHICLE_FAULTS, PERM_TRIGGER_EMERGENCY_SOS, PERM_VIEW_RECOVERY_INSTRUCTIONS,
        PERM_MANAGE_USERS, PERM_MANAGE_SYSTEM, PERM_VIEW_AUDIT_LOGS
    ]
}


# ==============================================================================
# 2. PASSWORD HASHING (PBKDF2-HMAC-SHA256 with Salt & Bcrypt/Argon2 Hooks)
# ==============================================================================

class PasswordHasher:
    """
    Standard library secure password hasher using PBKDF2 with SHA-256.
    Can be seamlessly swapped with bcrypt or argon2-cffi in production.
    """
    ITERATIONS = 100_000

    @classmethod
    def hash_password(cls, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """Returns (hex_salt, hex_hash)"""
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            cls.ITERATIONS
        )
        return salt.hex(), key.hex()

    @classmethod
    def verify_password(cls, password: str, salt_hex: str, hash_hex: str) -> bool:
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            cls.ITERATIONS
        )
        return secrets.compare_digest(key.hex(), hash_hex)


# ==============================================================================
# 3. DEMO USER DATABASE (Structured for relational / PostgreSQL migration)
# ==============================================================================

# Pre-generate salted hashes for demo accounts
_demo_salts_and_hashes = {
    "employee01": PasswordHasher.hash_password("Emp@123"),
    "manager01": PasswordHasher.hash_password("Mgr@123"),
    "operations01": PasswordHasher.hash_password("Ops@123"),
    "admin01": PasswordHasher.hash_password("Admin@123"),
}

DEMO_USERS_DATABASE: Dict[str, Dict[str, Any]] = {
    "employee01": {
        "id": "employee01",
        "name": "Employee01",
        "full_name": "Dave Miller",
        "role": ROLE_EMPLOYEE,
        "salt": _demo_salts_and_hashes["employee01"][0],
        "password_hash": _demo_salts_and_hashes["employee01"][1],
        "assigned_vehicle": "V23",
        "assigned_deliveries": ["D1045", "D1021", "D1022"],
        "department": "Fleet Operations - Sector East",
        "active": True
    },
    "manager01": {
        "id": "manager01",
        "name": "Manager01",
        "full_name": "Elena Rostova",
        "role": ROLE_LOGISTICS_MANAGER,
        "salt": _demo_salts_and_hashes["manager01"][0],
        "password_hash": _demo_salts_and_hashes["manager01"][1],
        "assigned_vehicle": None,
        "assigned_deliveries": [],
        "department": "Logistics Resilience & Network Strategy",
        "active": True
    },
    "operations01": {
        "id": "operations01",
        "name": "Operations01",
        "full_name": "Marcus Vance",
        "role": ROLE_OPERATIONS_MANAGER,
        "salt": _demo_salts_and_hashes["operations01"][0],
        "password_hash": _demo_salts_and_hashes["operations01"][1],
        "assigned_vehicle": None,
        "assigned_deliveries": [],
        "department": "Central Depot & Fleet Operations",
        "active": True
    },
    "admin01": {
        "id": "admin01",
        "name": "Admin01",
        "full_name": "System Administrator",
        "role": ROLE_SYSTEM_ADMIN,
        "salt": _demo_salts_and_hashes["admin01"][0],
        "password_hash": _demo_salts_and_hashes["admin01"][1],
        "assigned_vehicle": None,
        "assigned_deliveries": [],
        "department": "IT & Information Security Infrastructure",
        "active": True
    }
}


# ==============================================================================
# 4. SESSION & AUDIT MANAGER
# ==============================================================================

class AuthService:
    def __init__(self):
        # In-memory session store: token -> session dict
        # In production: Redis or signed encrypted JWT with expiration
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_ttl_seconds = 8 * 3600  # 8 hours session expiration
        self.audit_log: List[Dict[str, Any]] = []

    def log_audit(self, event_type: str, user_id: str, role: str, status: str, details: str):
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "user_id": user_id,
            "role": role,
            "status": status,
            "details": details
        }
        self.audit_log.append(event)
        # Keep log size bounded
        if len(self.audit_log) > 1000:
            self.audit_log.pop(0)

    def authenticate(self, user_id: str, password: str, selected_role: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates ID, password, and selected role.
        All three must match for authentication to succeed.
        Returns: (success, session_data_or_none, error_message_or_none)
        """
        clean_id = (user_id or "").strip().lower()
        clean_role = (selected_role or "").strip()

        if not clean_id or not password or not clean_role:
            self.log_audit("LOGIN_ATTEMPT", clean_id or "UNKNOWN", clean_role or "NONE", "REJECTED", "Missing required fields")
            return False, None, "Access Denied: Invalid ID, password, or role."

        user = DEMO_USERS_DATABASE.get(clean_id)
        if not user or not user.get("active", False):
            self.log_audit("LOGIN_ATTEMPT", clean_id, clean_role, "FAILED", "User ID not found")
            return False, None, "Access Denied: Invalid ID, password, or role."

        # Verify password hash
        if not PasswordHasher.verify_password(password, user["salt"], user["password_hash"]):
            self.log_audit("LOGIN_ATTEMPT", clean_id, clean_role, "FAILED", "Invalid password")
            return False, None, "Access Denied: Invalid ID, password, or role."

        # Verify selected role matches user's registered role
        if user["role"] != clean_role:
            self.log_audit("LOGIN_ATTEMPT", clean_id, clean_role, "FAILED", f"Role mismatch (expected {user['role']})")
            return False, None, "Access Denied: Invalid ID, password, or role."

        # Authentication successful: create cryptographically secure session
        token = secrets.token_hex(32)
        permissions = ROLE_PERMISSIONS.get(user["role"], [])
        
        session_info = {
            "token": token,
            "user_id": user["id"],
            "display_name": user["name"],
            "full_name": user["full_name"],
            "role": user["role"],
            "department": user["department"],
            "assigned_vehicle": user["assigned_vehicle"],
            "assigned_deliveries": user["assigned_deliveries"],
            "permissions": permissions,
            "created_at": time.time(),
            "expires_at": time.time() + self.session_ttl_seconds
        }

        self.active_sessions[token] = session_info
        self.log_audit("LOGIN_SUCCESS", clean_id, user["role"], "GRANTED", f"Session token created for {user['full_name']}")
        
        return True, session_info, None

    def validate_session(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Checks if session token is valid and not expired."""
        if not token or token not in self.active_sessions:
            return None
        session = self.active_sessions[token]
        if time.time() > session["expires_at"]:
            # Expired
            del self.active_sessions[token]
            self.log_audit("SESSION_EXPIRED", session["user_id"], session["role"], "TERMINATED", "Session expired due to TTL")
            return None
        return session

    def logout(self, token: Optional[str]) -> bool:
        """Destroys the authenticated session."""
        if token and token in self.active_sessions:
            session = self.active_sessions.pop(token)
            self.log_audit("LOGOUT", session["user_id"], session["role"], "TERMINATED", "User initiated logout")
            return True
        return False

    def authorize(self, token: Optional[str], required_permission: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Server-side authorization check."""
        session = self.validate_session(token)
        if not session:
            return False, None
        if required_permission in session.get("permissions", []):
            return True, session
        self.log_audit("AUTHORIZATION_FAILURE", session["user_id"], session["role"], "FORBIDDEN", f"Missing required permission: {required_permission}")
        return False, session


# Global singleton instance
auth_service = AuthService()
