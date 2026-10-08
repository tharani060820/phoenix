# Logistics Resilience Network (LRN)
## Graph-Based Adaptive Recovery System

> **A high-resilience AI logistics command-center command-center system that detects disruptions, analyzes multi-echelon ripple cascades via dependency graphs, ranks adaptive recovery strategies, and coordinates autonomous execution even under zero-connectivity offline conditions.**

---

## 🎯 System Architecture & Flow

The system visually demonstrates the complete closed-loop resilience lifecycle:

```mermaid
flowchart LR
    A["1. Normal Operations"] --> B["2. Disruption Event"]
    B --> C["3. Ripple Effect Analysis"]
    C --> D["4. AI Recovery Options"]
    D --> E["5. Automatic Coordination"]
    E --> F["6. Resilience Learning"]
    F --> A
```

---

## 🕸️ Advanced Dependency Graph (The Visual Centerpiece)

The Dependency Graph has been engineered into an **Enterprise-grade Topological Intelligence Engine** with the following advanced features:

### 1. Multi-Layout Engine Switcher
* **Multi-Echelon Columns**: Arranges nodes into 5 explicit horizontal supply chain tiers:
  $$\text{1. Warehouses (5)} \longrightarrow \text{2. Corridors (10)} \longrightarrow \text{3. Fleet (21)} \longrightarrow \text{4. Consignments} \longrightarrow \text{5. Clients (50)}$$
  Curved cubic Bezier links visually reveal downstream cascades with zero clutter.
* **Radial Cascade Mode**: Places the epicenter node (`Route R05` or selected node) at the center $(0,0)$ and projects 1-hop, 2-hop, and 3-hop dependents onto concentric radar distance perimeters.
* **Force Physics Mode**: Organic D3 force-directed physics with dynamic collision, link distances, and charge simulation.

### 2. Cascade Time-Machine Player (Scrubber & Auto-Play)
* An interactive scrubber with 7 sequential propagation stages:
  * **Step 0**: *T+00s Normal Baseline* — All 5 echelons operating at 98.2% on-time pace (All nodes Green).
  * **Step 1**: *T+10s Corridor R05 Blocked* — Collision at Mile 18; Route R05 capacity drops to 0% (Flashes Red).
  * **Step 2**: *T+25s Hauler V23 Breakdown* — Engine overheat (118°C) halts 18T Rig V23 in mountain cut (Turns Red).
  * **Step 3**: *T+40s Cryo Cargo D1045 Frozen* — Sub-zero vaccine payload at risk; SLA deadline 15:30 threatened (Turns Red/Orange).
  * **Step 4**: *T+55s Client C208 SLA Threat* — AcroTech BioLabs approaching contract breach; $2,450 penalty risk (Turns Orange).
  * **Step 5**: *T+60s AI Reroute Candidate Ready* — Standby Sprinter V27 via Connector R07 identified with 95% feasibility (Lights up in Purple).
  * **Step 6**: *RECOVERED Dynamic Rewire* — Edge atomic rewire executed; nodes transition to Healthy Green.

### 3. Dynamic Interactive Rewire (Live Graph Mutation)
* When clicking **⚡ COMMIT DYNAMIC REWIRE**:
  * The link between `V23` and `D1045` dissolves.
  * A glowing, animated green edge solidifies between `V27` ➔ `D1045`.
  * `D1045` and `C208` dynamically heal from 🔴 Red to 🟢 Emerald Green.
  * Confetti celebration triggers and live penalty risk drops to \$0!

### 4. Hardware-Accelerated Flow Particles & Shockwaves
* Animated energy photon particles flow smoothly along active links in the direction of cargo transit.
* Disrupted links show collision warnings and red pulse waves.
* Pulsing radar shockwave rings radiate outward from disrupted nodes.

### 5. Kinetic Breadcrumb Path Tracing
* Hovering or clicking any node isolates the end-to-end multi-echelon path from origin warehouse to destination client, dimming unrelated nodes to 15% opacity.
* Live breadcrumb banner displays:
  `Central Hub WH02 ➔ Highway 45 (R05) [BLOCKED] ➔ Rig V23 [BREAKDOWN] ➔ Cryo-Vaccine D1045 [AT RISK] ➔ AcroTech BioLabs (C208)`

### 6. Translucent Graph Topology HUD
* Floating telemetry overlay:
  * Critical Bottleneck: `Route R05` (Betweenness Centrality: `0.94`)
  * Mean Ripple Speed: `1.8 nodes / s`
  * Max Cascade Depth: `4 Echelons`
  * Hourly Exposure: `$2,450 / hr`

### 7. Advanced 3-Tab Node Inspector Drawer
* **Tab 1: Telemetry & State**: Live risk score progress gauge (0–100%), SLA countdown clock, cargo temperature (`-79.2°C` Cryo), payload weight, and contract penalty rate.
* **Tab 2: Topological Hierarchy**: Upstream parents list, downstream blast radius, and 1-click hop navigation.
* **Tab 3: AI Mitigations**: Ranked recovery options tailored to this node with 1-click **"⚡ Commit Rewire to V27"**.

---

## 🚀 Key Modules Overview

| Section | Key Features |
| :--- | :--- |
| **1. Overview Command System** | 6 live KPI cards, featured 🔴 **ROUTE 5 CLOSED** disruption card, multi-corridor status strip. |
| **2. Disruption Lens** | *"Understand what breaks before you decide what to fix."* Interactive what-if simulator (type, route, vehicle, severity, duration) with instant dynamic propagation. |
| **3. Advanced Dependency Graph** | Multi-Echelon Columns, Radial Cascade, Force Physics, Time-Machine player, dynamic edge rewire, and SVG particle dynamics. |
| **4. AI Recovery Engine** | Multi-criteria constraint ranking (Redirect, Reallocate, Reschedule, Partition, Defer) with explainable AI confidence scores (`95%`). |
| **5. Coordination Center** | Plan `#LRN-2048` dispatch execution, minute-by-minute timeline audit trail, and simulated WhatsApp (Driver) and SMS (VIP Customer) cards. |
| **6. Offline SOS Network** | Dead-zone emergency telemetry simulation with 868MHz LoRa / Satellite uplink, compact 64-byte JSON packet, and Ground Station `ACKNOWLEDGED` reception. |
| **7. Resilience Intelligence** | Evaluated metrics (1,842 strategies, 94.7% accuracy, 6.4m recovery time), heuristic distributions, and codified systemic learnings. |
| **8. Interactive Demo Mode** | Prominent **▶ START HACKATHON DEMO** button in header launching a **10-step guided tour** with step-by-step narration and automatic tab switching. |

---

## 📂 Project Architecture

```
lrn-recovery-system/
│
├── index.html                   # Authenticated command center (React 18, D3.js v7, Tailwind CSS, RBAC views)
├── auth.js                      # Client-side session lifecycle & WebCrypto SHA-256 fallback engine
├── auth_service.py              # Server-side authentication service (PBKDF2/bcrypt/Argon2 + RBAC matrix)
├── server.py                    # REST server with server-side authorization middleware
├── README.md                    # Project pitch guide, security architecture, and demo presentation script
│
├── data/
│   ├── networkData.js           # 100 Deliveries, 21 Vehicles, 10 Routes, 5 Warehouses, 50 Customers + Graph
│   └── disruptions.js           # Disruption catalog, recovery rankings, coordination plans & telemetry
│
└── database/
    └── neo4j_schema.cypher      # Production-grade Neo4j graph DDL, indexes, and Cypher traversal queries
```

---

## 🔐 Employee & Manager Login System (Strict Public Access Barrier)

The Logistics Resilience Network (LRN) enforces strict perimeter defense. The operational command center is **never** accessible to the unauthenticated public.

### Flow Architecture
```
Website Entry ──► Professional Login Page ──► Verify ID & Password (Hash) ──► Verify Role ──► Grant Access ──► Role-Tailored LRN Workspace
                                                      │
                                                      └── [Invalid Credentials / Role Mismatch]
                                                                    │
                                                                    ▼
                                                            "Access Denied: Invalid ID, password, or role."
```

### 🔑 Demonstration Credentials (For Evaluator Review)

| User ID | Registered Role | Password | Assigned Scope / Responsibilities |
| :--- | :--- | :--- | :--- |
| `employee01` | **Employee** | `Emp@123` | Assigned to Vehicle `V23` carrying cryo-vaccines `D1045`. View vehicle telemetry, consignments, report faults, trigger emergency SOS, and view driver recovery briefing. |
| `manager01` | **Logistics Manager** | `Mgr@123` | Network overview, view vehicles/routes/deliveries, analyze topological ripple effects, review recovery strategies, and **Approve Recovery Actions**. |
| `operations01` | **Operations Manager** | `Ops@123` | Full operational control, corridor capacity overrides, consignment expediting, run disruption simulations, and **Apply Recovery Actions** (live dynamic graph rewiring). |

> **Security Note:** In strict compliance with security requirements, passwords are never displayed on screen in the UI and must be entered by the user.

---

## 🛡️ Role-Based Access Control (RBAC) Workspaces

### 1. Employee Workspace (`employee01`)
* **View Assigned Vehicle Information**: Live diagnostics for Hauler `V23` (Engine Overheat alert `118°C`, speed `0 km/h`, fuel `64%`, location `Mile 18 Mountain Cut`).
* **View Assigned Delivery Information**: Status of 3 onboard consignments: Cryo-Vaccines `D1045` (`-79.2°C`, SLA `15:30`), Surgical Kits `D1021`, and Optical Sensors `D1022`.
* **Report Vehicle Faults**: Interactive fault submission form dispatching real-time tickets (e.g. `FLT-9821`) directly to Central Logistics Command.
* **Trigger Emergency SOS**: Embedded 868MHz LoRa mesh / Satellite burst transmitter with live ground station acknowledgement.
* **View Relevant Recovery Instructions**: Driver incident protocol detailing Mile 18 containment, dry-ice preservation, and cross-docking rendezvous with Relief Sprinter `V27`.

### 2. Logistics Manager Workspace (`manager01`)
* **View Vehicles, Corridors & Deliveries**: Network-wide health monitoring.
* **Analyze Ripple Effects**: Multi-layout dependency graph and cascade time-machine.
* **Review Recovery Strategies**: AI multi-criteria ranked options.
* **Approve Recovery Actions**: Formal manager sign-off on recovery plans.
* **Emergency Events Monitoring**: Real-time distress telemetry and driver fault stream.

### 3. Operations Manager Workspace (`operations01`)
* **Manage Fleet & Corridors**: Dynamic corridor status toggling (`OPEN`, `RESTRICTED`, `CLOSED`), speed limit adjustments, and vehicle fleet dispatch.
* **Manage Deliveries**: Expedite priority consignments and reroute destination hubs.
* **Disruption Simulator**: Run what-if simulations with configurable route, vehicle, severity, and duration.
* **Apply Recovery Actions**: Full authority to execute atomic graph edge mutations (**Commit Dynamic Rewire**).
* **Operations Control Center**: Manage global sorting caps and resilience thresholds.

### 4. System Administrator (Architectural Provision)
* Extensible role structure (`ROLE_SYSTEM_ADMIN`) provisioned in `auth_service.py` for enterprise user directory management, audit trail inspection, and system policies.

---

## 🔒 Security Architecture Blueprint

* **Transport Security**: Ready for HTTPS / TLS 1.3 with HSTS headers.
* **Password Hashing**: PBKDF2-HMAC-SHA256 with 100,000 rounds and unique per-user cryptographically random salts; drop-in interfaces for Argon2id and Bcrypt.
* **Session Lifecycle**: High-entropy 256-bit Bearer tokens with 8-hour TTL and server-side revocation on **Logout**.
* **Server-Side Authorization**: API routes on `server.py` enforce role permissions before executing mutations (e.g. employees calling `/recoveries/apply` receive HTTP 403 Forbidden).
* **Tamper-Evident Audit Stream**: Every login attempt, permission escalation, fault report, and recovery commit is logged with timestamp, user ID, role, and IP.

---

## ⚡ How to Run the Command System

### Option A: Run with Python Server (Recommended — REST APIs + Static Serving)
Run the zero-dependency Python server:
```powershell
cd C:\Users\thara\.gemini\antigravity\scratch\lrn-recovery-system
python server.py
```
Then visit:
👉 **`http://localhost:8000`**

### Option B: Standalone Browser Launch
Open the file in Chrome, Edge, or any modern browser:
```
file:///C:/Users/thara/.gemini/antigravity/scratch/lrn-recovery-system/index.html
```

### Available REST Endpoints on `server.py`:
* `POST /api/auth/login` — Authenticate user ID, password, and role; issue bearer token
* `POST /api/auth/logout` — Terminate and revoke authenticated session
* `GET  /api/auth/session` — Validate session token and retrieve authenticated profile
* `POST /api/faults/report` — Log vehicle fault ticket from driver terminal
* `POST /api/recoveries/apply` — Atomic graph edge rewiring transaction (Manager authorized)
* `POST /api/disruptions/simulate` — Dynamic multi-hop ripple cascade computation
* `POST /api/sos/transmit` — Emergency LoRa/Satellite SOS packet transmission
* `GET  /api/health` — System health, auth engine, and LoRa mesh status

