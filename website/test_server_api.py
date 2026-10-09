"""
Test suite for LRN Server & Authentication APIs
"""
import urllib.request
import urllib.error
import json
import time
import subprocess
import sys
import os

SERVER_URL = "http://localhost:8000"

def make_request(path, method="GET", data=None, token=None):
    url = f"{SERVER_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        return 0, str(e)

def run_tests():
    print("Testing LRN Authentication & RBAC APIs...")
    
    # 1. Health check
    status, data = make_request("/api/health")
    print(f"1. Health Check: Status {status}, System: {data.get('system')}")
    assert status == 200
    
    # 2. Test Invalid Credentials
    status, data = make_request("/api/auth/login", method="POST", data={
        "id": "employee01",
        "password": "WrongPassword",
        "role": "Employee"
    })
    print(f"2. Invalid Password: Status {status}, Error: {data.get('error')}")
    assert status == 401
    assert data.get("error") == "Access Denied: Invalid ID, password, or role."
    
    # 3. Test Role Mismatch
    status, data = make_request("/api/auth/login", method="POST", data={
        "id": "employee01",
        "password": "Emp@123",
        "role": "Logistics Manager"
    })
    print(f"3. Role Mismatch: Status {status}, Error: {data.get('error')}")
    assert status == 401
    assert data.get("error") == "Access Denied: Invalid ID, password, or role."

    # 4. Test Valid Employee Login
    status, emp_data = make_request("/api/auth/login", method="POST", data={
        "id": "employee01",
        "password": "Emp@123",
        "role": "Employee"
    })
    print(f"4. Employee Login: Status {status}, Welcome: {emp_data.get('message')}")
    assert status == 200
    emp_token = emp_data["token"]
    assert emp_data["user"]["role"] == "Employee"
    assert emp_data["user"]["assigned_vehicle"] == "V23"

    # 5. Test Valid Logistics Manager Login
    status, mgr_data = make_request("/api/auth/login", method="POST", data={
        "id": "manager01",
        "password": "Mgr@123",
        "role": "Logistics Manager"
    })
    print(f"5. Manager Login: Status {status}, Welcome: {mgr_data.get('message')}")
    assert status == 200
    mgr_token = mgr_data["token"]
    assert mgr_data["user"]["role"] == "Logistics Manager"

    # 6. Test Valid Operations Manager Login
    status, ops_data = make_request("/api/auth/login", method="POST", data={
        "id": "operations01",
        "password": "Ops@123",
        "role": "Operations Manager"
    })
    print(f"6. Operations Login: Status {status}, Welcome: {ops_data.get('message')}")
    assert status == 200
    ops_token = ops_data["token"]
    assert ops_data["user"]["role"] == "Operations Manager"

    # 7. Test Server-Side Authorization: Employee attempting privileged recovery action
    status, data = make_request("/api/recoveries/apply", method="POST", data={
        "plan_id": "LRN-2048",
        "strategy": "REDIRECT"
    }, token=emp_token)
    print(f"7. Server-Side RBAC Guard (Employee calling /recoveries/apply): Status {status}, Error: {data.get('error')}")
    assert status == 403

    # 8. Test Server-Side Authorization: Operations Manager applying recovery
    status, data = make_request("/api/recoveries/apply", method="POST", data={
        "plan_id": "LRN-2048",
        "strategy": "REDIRECT"
    }, token=ops_token)
    print(f"8. Server-Side RBAC (Operations Manager calling /recoveries/apply): Status {status}, Result: {data.get('status')}")
    assert status == 200
    assert data.get("status") == "APPLIED"

    # 9. Test Employee Reporting Vehicle Fault
    status, data = make_request("/api/faults/report", method="POST", data={
        "category": "Engine Overheat / Coolant Rupture",
        "severity": "CRITICAL",
        "location": "Route R05, Mile 18 Mountain Cut",
        "description": "Temperature at 118C."
    }, token=emp_token)
    print(f"9. Employee Reporting Fault: Status {status}, Ticket: {data.get('ticket_id')}")
    assert status == 200
    assert data.get("ticket_id") is not None

    # 10. Test Logout
    status, data = make_request("/api/auth/logout", method="POST", token=emp_token)
    print(f"10. Logout: Status {status}, Msg: {data.get('message')}")
    assert status == 200

    # 11. Verify Revoked Token Rejected After Logout
    status, data = make_request("/api/auth/session", method="GET", token=emp_token)
    print(f"11. Session Check with Revoked Token: Status {status}")
    assert status == 401

    print("\n>>> ALL 11 BACKEND SECURITY & RBAC TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    # Start server process
    proc = subprocess.Popen([sys.executable, "server.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
    started = False
    for _ in range(25):
        time.sleep(0.4)
        try:
            with urllib.request.urlopen("http://localhost:8000/api/health", timeout=1) as resp:
                if resp.status == 200:
                    started = True
                    break
        except Exception:
            pass
    if not started:
        print("Error: Server failed to start within timeout.")
        proc.terminate()
        sys.exit(1)
    try:
        run_tests()
    finally:
        proc.terminate()
        proc.wait()
