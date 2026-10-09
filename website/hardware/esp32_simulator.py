"""
Logistics Resilience Network (LRN) - ESP32 Hardware Simulator
Simulates physical ESP32 terminal sending emergency telemetry to LRN Central Command.
Zero external dependencies (uses standard library urllib.request).
"""
import sys
import json
import time
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_URL = "http://127.0.0.1:8000/disruptions"

def send_esp32_packet(
    vehicle_id: str = "V23",
    event_type: str = "VEHICLE_FAULT",
    signal_status: str = "NO_SIGNAL",
    source: str = "LoRa/Satellite",
    priority: str = "EMERGENCY",
    server_url: str = DEFAULT_URL
):
    payload = {
        "vehicleID": vehicle_id,
        "event": event_type,
        "signalStatus": signal_status,
        "source": source,
        "priority": priority,
        "route": "R05",
        "location": "11.0168,76.9558",
        "notes": "Transmission originating from onboard ESP32 hardware transceiver."
    }

    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        server_url,
        data=data_bytes,
        headers={"Content-Type": "application/json"}
    )

    print("\n=======================================================")
    print(f"📡 [ESP32 HARDWARE SIMULATOR] Transmitting to {server_url}")
    print("=======================================================")
    print(json.dumps(payload, indent=2))
    print("-------------------------------------------------------")

    try:
        start_t = time.time()
        with urllib.request.urlopen(req, timeout=5) as response:
            latency_ms = int((time.time() - start_t) * 1000)
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print(f"✅ [ACK RECEIVED - {response.status} OK] Latency: {latency_ms}ms")
            print(f"Disruption Registered: {res_json.get('disruption_id', 'N/A')}")
            print(f"Status: {res_json.get('status')}")
            rec = res_json.get('decision_recommendation', {})
            if rec:
                print(f"Recommended Action: {rec.get('title')}")
                print(f"Composite Score: {rec.get('scores', {}).get('composite_score')}")
            return res_json
    except urllib.error.URLError as e:
        print(f"❌ [TRANSMISSION ERROR] Could not reach server: {e}")
        return None

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fault"
    if mode == "sos":
        send_esp32_packet(event_type="EMERGENCY_SOS", signal_status="NO_SIGNAL", source="LoRa/Satellite", priority="EMERGENCY")
    elif mode == "connected":
        send_esp32_packet(event_type="VEHICLE_FAULT", signal_status="CONNECTED_4G", source="Wi-Fi/4G-LTE", priority="HIGH")
    else:
        # Default match to user prompt
        send_esp32_packet(event_type="VEHICLE_FAULT", signal_status="NO_SIGNAL", source="LoRa/Satellite", priority="EMERGENCY")
