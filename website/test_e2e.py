import urllib.request
import urllib.error
import json
import sys

def test():
    print("========================================================")
    print("LRN END-TO-END VERIFICATION TEST SUITE")
    print("========================================================")

    # 1. UI Root
    req = urllib.request.Request("http://127.0.0.1:8000/")
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 200
        html = resp.read().decode("utf-8")
        assert "Logistics Resilience Network" in html
        print("[PASS] 1. Web UI Root (index.html) -> 200 OK")

    # 2. Health
    req = urllib.request.Request("http://127.0.0.1:8000/api/health")
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        assert data.get("status") == "ONLINE"
        print("[PASS] 2. System Health Check -> 200 OK (Status: ONLINE)")

    # 3. Manager JWT Auth
    auth_body = {"id": "manager01", "password": "Mgr@123", "role": "Logistics Manager"}
    req = urllib.request.Request("http://127.0.0.1:8000/auth", data=json.dumps(auth_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        auth_data = json.loads(resp.read().decode("utf-8"))
        token = auth_data["token"]
        name = auth_data["user"]["display_name"]
        role = auth_data["user"]["role"]
        print(f"[PASS] 3. JWT Login -> 200 OK (User: {name}, Role: {role})")

    # 4. Deliveries
    req = urllib.request.Request("http://127.0.0.1:8000/deliveries", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        deliv_data = json.loads(resp.read().decode("utf-8"))
        assert len(deliv_data["deliveries"]) > 0
        del_count = len(deliv_data["deliveries"])
        veh_count = len(deliv_data["vehicles"])
        print(f"[PASS] 4. Deliveries Query -> 200 OK ({del_count} Deliveries, {veh_count} Vehicles)")

    # 5. ESP32 SOS Disruption Ingestion
    esp32_packet = {
        "vehicleID": "V23",
        "event": "VEHICLE_FAULT",
        "signalStatus": "NO_SIGNAL",
        "source": "LoRa/Satellite",
        "priority": "EMERGENCY"
    }
    req = urllib.request.Request("http://127.0.0.1:8000/disruptions", data=json.dumps(esp32_packet).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        disr_data = json.loads(resp.read().decode("utf-8"))
        status = disr_data["status"]
        rec_title = disr_data.get("recommended_action", {}).get("title", "")
        print(f"[PASS] 5. ESP32 SOS Ingestion -> 200 OK (Status: {status}, Recommended: {rec_title})")

    # 6. Recovery Strategy Generation (5 Canonical Strategies)
    req = urllib.request.Request("http://127.0.0.1:8000/recovery?disruption_id=DISR-2026-081")
    with urllib.request.urlopen(req, timeout=5) as resp:
        rec_data = json.loads(resp.read().decode("utf-8"))
        strategies = [s["strategy"] for s in rec_data["ranked_strategies"]]
        assert set(strategies) == {"redirect", "reallocate", "reschedule", "partition", "defer"}
        print(f"[PASS] 6. Decision Engine 5 Strategies -> 200 OK (Ranked: {strategies})")

    # 7. Apply Recovery Action (SQL Adaptive Learning Record)
    apply_body = {"plan_id": "LRN-2048", "strategy": "reallocate"}
    req = urllib.request.Request("http://127.0.0.1:8000/recoveries/apply", data=json.dumps(apply_body).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        apply_data = json.loads(resp.read().decode("utf-8"))
        assert apply_data.get("status") in ["APPROVED", "APPLIED", "SUCCESS"]
        out_id = apply_data.get("sql_outcome_id") or apply_data.get("outcome_id")
        print(f"[PASS] 7. Apply Recovery Plan -> 200 OK (Status: {apply_data.get('status')}, Outcome ID: {out_id})")

    # 8. Adaptive Learning Stats
    req = urllib.request.Request("http://127.0.0.1:8000/adaptive-learning/stats")
    with urllib.request.urlopen(req, timeout=5) as resp:
        stats_data = json.loads(resp.read().decode("utf-8"))
        kpis = stats_data["kpis"]
        tot = kpis["total_recovery_actions_recorded"]
        succ = kpis["overall_success_rate"]
        print(f"[PASS] 8. SQL Adaptive Learning Stats -> 200 OK (Total Recorded: {tot}, Success Rate: {succ})")

    print("========================================================")
    print(">>> ALL 8 CORE CAPABILITIES FULLY OPERATIONAL! <<<")
    print("========================================================")

if __name__ == "__main__":
    test()
