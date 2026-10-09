/**
 * Logistics Resilience Network (LRN) - Authentication & RBAC Client Engine
 * 
 * Provides:
 * - Session lifecycle management (Create, Validate, Terminate)
 * - Server API integration (/api/auth/login, /api/auth/logout, /api/auth/session)
 * - Offline/standalone fallback authentication using SHA-256 validation
 * - Role-Based Access Control (RBAC) permission evaluation
 * - Complete security architecture specification for production migration
 */

(function (window) {
  'use strict';

  // ===========================================================================
  // 1. ROLES & PERMISSIONS
  // ===========================================================================
  const ROLES = {
    EMPLOYEE: 'Employee',
    LOGISTICS_MANAGER: 'Logistics Manager',
    OPERATIONS_MANAGER: 'Operations Manager',
    SYSTEM_ADMIN: 'System Administrator'
  };

  const PERMISSIONS = {
    // Employee permissions
    VIEW_ASSIGNED_VEHICLE: 'view_assigned_vehicle',
    VIEW_ASSIGNED_DELIVERY: 'view_assigned_delivery',
    REPORT_VEHICLE_FAULTS: 'report_vehicle_faults',
    TRIGGER_EMERGENCY_SOS: 'trigger_emergency_sos',
    VIEW_RECOVERY_INSTRUCTIONS: 'view_recovery_instructions',

    // Logistics Manager permissions
    VIEW_VEHICLES: 'view_vehicles',
    VIEW_ROUTES: 'view_routes',
    VIEW_DELIVERIES: 'view_deliveries',
    VIEW_DISRUPTIONS: 'view_disruptions',
    ANALYZE_RIPPLE_EFFECTS: 'analyze_ripple_effects',
    VIEW_RECOVERY_STRATEGIES: 'view_recovery_strategies',
    APPROVE_RECOVERY_ACTIONS: 'approve_recovery_actions',
    VIEW_EMERGENCY_EVENTS: 'view_emergency_events',

    // Operations Manager permissions
    MANAGE_VEHICLES: 'manage_vehicles',
    MANAGE_ROUTES: 'manage_routes',
    MANAGE_DELIVERIES: 'manage_deliveries',
    APPLY_RECOVERY_ACTIONS: 'apply_recovery_actions',
    MONITOR_DISRUPTION_EVENTS: 'monitor_disruption_events',
    MANAGE_OPERATIONAL_INFO: 'manage_operational_info',

    // System Administrator extensions
    MANAGE_USERS: 'manage_users',
    MANAGE_SYSTEM: 'manage_system',
    VIEW_AUDIT_LOGS: 'view_audit_logs'
  };

  const ROLE_PERMISSIONS = {
    [ROLES.EMPLOYEE]: [
      PERMISSIONS.VIEW_ASSIGNED_VEHICLE,
      PERMISSIONS.VIEW_ASSIGNED_DELIVERY,
      PERMISSIONS.REPORT_VEHICLE_FAULTS,
      PERMISSIONS.TRIGGER_EMERGENCY_SOS,
      PERMISSIONS.VIEW_RECOVERY_INSTRUCTIONS
    ],
    [ROLES.LOGISTICS_MANAGER]: [
      PERMISSIONS.VIEW_VEHICLES,
      PERMISSIONS.VIEW_ROUTES,
      PERMISSIONS.VIEW_DELIVERIES,
      PERMISSIONS.VIEW_DISRUPTIONS,
      PERMISSIONS.ANALYZE_RIPPLE_EFFECTS,
      PERMISSIONS.VIEW_RECOVERY_STRATEGIES,
      PERMISSIONS.APPROVE_RECOVERY_ACTIONS,
      PERMISSIONS.VIEW_EMERGENCY_EVENTS,
      PERMISSIONS.VIEW_ASSIGNED_VEHICLE,
      PERMISSIONS.VIEW_ASSIGNED_DELIVERY
    ],
    [ROLES.OPERATIONS_MANAGER]: [
      PERMISSIONS.MANAGE_VEHICLES,
      PERMISSIONS.MANAGE_ROUTES,
      PERMISSIONS.MANAGE_DELIVERIES,
      PERMISSIONS.APPLY_RECOVERY_ACTIONS,
      PERMISSIONS.MONITOR_DISRUPTION_EVENTS,
      PERMISSIONS.MANAGE_OPERATIONAL_INFO,
      PERMISSIONS.VIEW_VEHICLES,
      PERMISSIONS.VIEW_ROUTES,
      PERMISSIONS.VIEW_DELIVERIES,
      PERMISSIONS.VIEW_DISRUPTIONS,
      PERMISSIONS.ANALYZE_RIPPLE_EFFECTS,
      PERMISSIONS.VIEW_RECOVERY_STRATEGIES,
      PERMISSIONS.VIEW_EMERGENCY_EVENTS
    ],
    [ROLES.SYSTEM_ADMIN]: Object.values(PERMISSIONS)
  };

  // ===========================================================================
  // 2. CRYPTOGRAPHIC UTILITIES (Web Crypto API SHA-256 for standalone mode)
  // ===========================================================================
  async function computeSha256(text) {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // Pre-hashed verification signatures for prototype standalone fallback
  // employee01:Emp@123, manager01:Mgr@123, operations01:Ops@123
  const DEMO_SIGNATURES = {
    'employee01': {
      // SHA-256 of "employee01:Emp@123:lrn_salt_v2"
      token: '8cf8f82851aefa37b1be7a9796393a63fc82ed83df22bb65bfd69f6c0b7932d8',
      name: 'Employee01',
      fullName: 'Dave Miller',
      role: ROLES.EMPLOYEE,
      assignedVehicle: 'V23',
      assignedDeliveries: ['D1045', 'D1021', 'D1022'],
      department: 'Fleet Operations - Sector East'
    },
    'manager01': {
      // SHA-256 of "manager01:Mgr@123:lrn_salt_v2"
      token: '60fbf02c2dcf8b94d2465abb33bdf00c8370ec4af23683c24d9171ad84f43c38',
      name: 'Manager01',
      fullName: 'Elena Rostova',
      role: ROLES.LOGISTICS_MANAGER,
      assignedVehicle: null,
      assignedDeliveries: [],
      department: 'Logistics Resilience & Network Strategy'
    },
    'operations01': {
      // SHA-256 of "operations01:Ops@123:lrn_salt_v2"
      token: 'a7d5b48a6250e468049cffcf3f5cb9dc5a769bce4203d759ae1ebfcc15c1227c',
      name: 'Operations01',
      fullName: 'Marcus Vance',
      role: ROLES.OPERATIONS_MANAGER,
      assignedVehicle: null,
      assignedDeliveries: [],
      department: 'Central Depot & Fleet Operations'
    }
  };

  const SESSION_STORAGE_KEY = 'lrn_authenticated_session';

  // ===========================================================================
  // 3. AUTH SERVICE IMPLEMENTATION
  // ===========================================================================
  const LRNAuth = {
    ROLES,
    PERMISSIONS,
    ROLE_PERMISSIONS,

    /**
     * Authenticate user with ID, password, and selected role.
     * Communicates with backend REST API if online, or uses cryptographic verification fallback.
     */
    async login(userId, password, role) {
      const cleanId = (userId || '').trim().toLowerCase();
      const cleanRole = (role || '').trim();
      const rawPassword = password || '';

      if (!cleanId || !rawPassword || !cleanRole) {
        return {
          success: false,
          error: 'Access Denied: Invalid ID, password, or role.'
        };
      }

      // 1. Try Backend REST API first
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: cleanId,
            password: rawPassword,
            role: cleanRole
          })
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.user) {
            const sessionData = {
              token: data.token,
              userId: data.user.user_id || cleanId,
              displayName: data.user.display_name || (cleanId.charAt(0).toUpperCase() + cleanId.slice(1)),
              fullName: data.user.full_name,
              role: data.user.role,
              department: data.user.department,
              assignedVehicle: data.user.assigned_vehicle,
              assignedDeliveries: data.user.assigned_deliveries || [],
              permissions: data.user.permissions || ROLE_PERMISSIONS[cleanRole] || [],
              loginTime: new Date().toISOString(),
              expiresAt: data.user.expires_at || (Date.now() + 8 * 3600 * 1000)
            };
            this.setSession(sessionData);
            return { success: true, session: sessionData };
          }
        } else if (response.status === 401 || response.status === 403) {
          // Explicit rejection from backend
          return {
            success: false,
            error: 'Access Denied: Invalid ID, password, or role.'
          };
        }
      } catch (err) {
        // Backend not reachable (e.g. running via file:// or server offline). Proceed to fallback.
      }

      // 2. Standalone / Offline Cryptographic Verification Fallback
      const targetUser = DEMO_SIGNATURES[cleanId];
      if (!targetUser) {
        return {
          success: false,
          error: 'Access Denied: Invalid ID, password, or role.'
        };
      }

      // Role check
      if (targetUser.role !== cleanRole) {
        return {
          success: false,
          error: 'Access Denied: Invalid ID, password, or role.'
        };
      }

      // Hash comparison
      const computedHash = await computeSha256(`${cleanId}:${rawPassword}:lrn_salt_v2`);
      if (computedHash !== targetUser.token) {
        return {
          success: false,
          error: 'Access Denied: Invalid ID, password, or role.'
        };
      }

      // Successful local authentication
      const sessionData = {
        token: 'local_sec_' + Math.random().toString(36).substring(2) + Date.now().toString(36),
        userId: cleanId,
        displayName: targetUser.name,
        fullName: targetUser.fullName,
        role: targetUser.role,
        department: targetUser.department,
        assignedVehicle: targetUser.assignedVehicle,
        assignedDeliveries: targetUser.assignedDeliveries,
        permissions: ROLE_PERMISSIONS[targetUser.role] || [],
        loginTime: new Date().toISOString(),
        expiresAt: Date.now() + 8 * 3600 * 1000
      };

      this.setSession(sessionData);
      return { success: true, session: sessionData };
    },

    /**
     * Terminate authenticated session
     */
    async logout() {
      const session = this.getSession();
      if (session && session.token) {
        try {
          await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${session.token}`
            }
          });
        } catch (e) {
          // Ignore network errors on logout
        }
      }
      this.clearSession();
      return { success: true };
    },

    /**
     * Retrieve active session from sessionStorage
     */
    getSession() {
      try {
        const raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
        if (!raw) return null;
        const session = JSON.parse(raw);
        if (session.expiresAt && Date.now() > session.expiresAt) {
          this.clearSession();
          return null;
        }
        return session;
      } catch (e) {
        return null;
      }
    },

    /**
     * Save active session
     */
    setSession(session) {
      try {
        sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
      } catch (e) {
        console.error('Failed to store session in sessionStorage', e);
      }
    },

    /**
     * Destroy stored session
     */
    clearSession() {
      try {
        sessionStorage.removeItem(SESSION_STORAGE_KEY);
      } catch (e) {
        console.error('Failed to clear session', e);
      }
    },

    /**
     * Check if active user has a specific permission
     */
    hasPermission(permission) {
      const session = this.getSession();
      if (!session) return false;
      const permissions = session.permissions || ROLE_PERMISSIONS[session.role] || [];
      return permissions.includes(permission);
    },

    /**
     * Check if active user has one of the allowed roles
     */
    hasRole(rolesList) {
      const session = this.getSession();
      if (!session) return false;
      if (Array.isArray(rolesList)) {
        return rolesList.includes(session.role);
      }
      return session.role === rolesList;
    },

    /**
     * Security Architecture Blueprint & Production Implementation Matrix
     */
    getSecurityArchitecture() {
      return {
        title: 'LRN Enterprise Security Architecture Blueprint',
        version: '2.4-PROD-READY',
        layers: [
          {
            name: 'Transport Security',
            technology: 'TLS 1.3 / HTTPS',
            spec: 'Enforced HSTS, secure cookies (SameSite=Strict, Secure, HttpOnly), cipher suites TLS_AES_256_GCM_SHA384'
          },
          {
            name: 'Password & Credential Hashing',
            technology: 'Argon2id / Bcrypt / PBKDF2',
            spec: 'Argon2id with m=65536, t=3, p=4 or PBKDF2-HMAC-SHA256 with 100,000 rounds and 32-byte cryptographically secure salts'
          },
          {
            name: 'Session & Token Lifecycle',
            technology: 'Opaque Revocable Tokens / JWT RS256',
            spec: 'High-entropy 256-bit cryptographically random tokens stored in Redis with 8-hour sliding TTL and instant server-side revocation on logout'
          },
          {
            name: 'Role-Based Access Control (RBAC)',
            technology: 'Granular Matrix Authorization',
            spec: 'Strict principle of least privilege. Every route, API endpoint, and mutation independently verified on server side'
          },
          {
            name: 'Server-Side Authorization',
            technology: 'Middleware Interceptors',
            spec: 'Zero frontend-only trust. Endpoints verify token validity and role permission before database or graph mutation'
          },
          {
            name: 'Tamper-Evident Audit Logging',
            technology: 'Append-Only Event Stream',
            spec: 'Every login attempt, permission escalation, recovery commit, fault submission, and SOS trigger is logged with timestamp, user ID, role, and IP'
          }
        ]
      };
    }
  };

  // Expose to window
  window.LRNAuth = LRNAuth;

})(window);
