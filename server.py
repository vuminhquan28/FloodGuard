import http.server
import socketserver
import urllib.parse
import json
import time
import threading
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Live System State
state_lock = threading.Lock()
system_state = {
    "water": 15,
    "distance": 8.8,
    "rain": False,
    "rain_adc": 3850,
    "state": "NORMAL",
    "mode": "AUTO",
    "pump": False,
    "valve": 0,
    "buzzer": "OFF",
    "sensor_fault": False,
    "last_client_request": time.time(),
    "critical_start_time": None,
    "pump_start_time": 0,
    "failsafe_triggered": False
}

def fsm_worker():
    """Background engine simulating ESP32 FSM logic every 100ms"""
    while True:
        time.sleep(0.1)
        with state_lock:
            now = time.time()
            s = system_state
            
            # Check sensor fault
            if s["sensor_fault"]:
                s["state"] = "SENSOR_FAULT"
                s["pump"] = False
                s["valve"] = 50
                s["buzzer"] = "SLOW"
                continue

            # In MANUAL Mode: check Failsafe & Safety Override
            if s["mode"] == "MANUAL":
                # Failsafe 30s timeout
                if now - s["last_client_request"] > 30.0:
                    s["mode"] = "AUTO"
                    s["failsafe_triggered"] = True
                    print(f"[{time.strftime('%H:%M:%S')}] Failsafe 30s Timeout triggered: Reverted to AUTO mode.")
                
                # Emergency Safety Override: if water >= 56% for > 10s
                if s["water"] >= 56:
                    if s["critical_start_time"] is None:
                        s["critical_start_time"] = now
                    elif now - s["critical_start_time"] > 10.0 and (not s["pump"] or s["valve"] < 100):
                        s["mode"] = "AUTO"
                        s["pump"] = True
                        s["valve"] = 100
                        s["state"] = "CRITICAL"
                        s["buzzer"] = "CONTINUOUS"
                        print(f"[{time.strftime('%H:%M:%S')}] Emergency Safety Override 10s: Reverted to AUTO, Pump 100%, Valve 100%.")
                else:
                    s["critical_start_time"] = None

            # State Transitions with 3% Hysteresis (luôn đánh giá để Đèn & Còi tự động cảnh báo)
            is_submerged = s["rain_adc"] < 1100
            is_heavy = s["rain_adc"] < 1800
            is_light = s["rain"] or s["rain_adc"] < 3200
            w = s["water"]
            curr_state = s["state"]

            if curr_state == "CRITICAL":
                if w < 53 and not is_submerged:
                    s["state"] = "DANGER"
            elif curr_state == "DANGER":
                if w >= 56 or is_submerged:
                    s["state"] = "CRITICAL"
                elif w < 35 and not is_heavy:
                    s["state"] = "WARNING"
            elif curr_state == "WARNING":
                if w >= 56 or is_submerged:
                    s["state"] = "CRITICAL"
                elif w >= 38 or is_heavy:
                    s["state"] = "DANGER"
                elif w < 16 and not is_light:
                    s["state"] = "NORMAL"
            else: # NORMAL
                if w >= 56 or is_submerged:
                    s["state"] = "CRITICAL"
                elif w >= 38 or is_heavy:
                    s["state"] = "DANGER"
                elif w >= 19 or is_light:
                    s["state"] = "WARNING"

            # Cập nhật còi báo động theo trạng thái ở cả AUTO và MANUAL
            st = s["state"]
            if st == "CRITICAL":
                s["buzzer"] = "CONTINUOUS"
            elif st == "DANGER":
                s["buzzer"] = "FAST"
            elif st == "WARNING":
                s["buzzer"] = "SLOW"
            else:
                s["buzzer"] = "OFF"

            # Chỉ gán Bơm và Van tự động khi ở chế độ AUTO
            if s["mode"] == "AUTO":
                if st == "CRITICAL":
                    s["pump"] = True
                    s["valve"] = 100
                elif st == "DANGER":
                    s["pump"] = True if w >= 20 else False
                    s["valve"] = 50
                elif st == "WARNING":
                    s["pump"] = False
                    s["valve"] = 0
                else: # NORMAL
                    s["pump"] = False
                    s["valve"] = 0


class FloodGuardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API: /api/status
        if path == "/api/status":
            with state_lock:
                system_state["last_client_request"] = time.time()
                data = {
                    "water": system_state["water"],
                    "distance": system_state["distance"],
                    "state": system_state["state"],
                    "mode": system_state["mode"],
                    "rain": system_state["rain"],
                    "rain_adc": system_state["rain_adc"],
                    "pump": 1 if system_state["pump"] else 0,
                    "valve": system_state["valve"],
                    "buzzer": system_state["buzzer"],
                    "failsafe": system_state["failsafe_triggered"]
                }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        # 2. API: /api/control
        if path == "/api/control":
            with state_lock:
                system_state["last_client_request"] = time.time()
                system_state["failsafe_triggered"] = False
                
                # Check action query
                action = query.get("action", [None])[0]
                mode_param = query.get("mode", [None])[0]
                pump_param = query.get("pump", [None])[0]
                valve_param = query.get("valve", [None])[0]

                if mode_param:
                    system_state["mode"] = mode_param.upper()
                if action == "mode_toggle":
                    system_state["mode"] = "MANUAL" if system_state["mode"] == "AUTO" else "AUTO"

                if action in ["pump_toggle", "valve_cycle", "valve_toggle", "valve_mode", "valve_0", "valve_50", "valve_100"] or pump_param or valve_param:
                    system_state["mode"] = "MANUAL"

                if system_state["mode"] == "MANUAL":
                    if action == "pump_toggle" or pump_param == "toggle":
                        system_state["pump"] = not system_state["pump"]
                    elif pump_param in ["1", "on"]:
                        system_state["pump"] = True
                    elif pump_param in ["0", "off"]:
                        system_state["pump"] = False

                    # Valve control: support cycle/toggle, percentages (0, 50, 100), and degrees (0, 90, 180)
                    if action in ["valve_cycle", "valve_toggle", "valve_mode"] or valve_param in ["cycle", "toggle"]:
                        if system_state["valve"] == 0:
                            system_state["valve"] = 50
                        elif system_state["valve"] == 50:
                            system_state["valve"] = 100
                        else:
                            system_state["valve"] = 0
                    elif action == "valve_0" or valve_param in ["0", "0deg"]:
                        system_state["valve"] = 0
                    elif action == "valve_50" or valve_param in ["50", "90", "90deg"]:
                        system_state["valve"] = 50
                    elif action == "valve_100" or valve_param in ["100", "180", "180deg"]:
                        system_state["valve"] = 100
                
                resp = {"status": "OK", "mode": system_state["mode"], "pump": system_state["pump"], "valve": system_state["valve"]}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # 3. API: /api/simulate
        if path == "/api/simulate":
            with state_lock:
                if "water" in query:
                    val = max(0, min(100, int(query["water"][0])))
                    system_state["water"] = val
                    system_state["distance"] = round(10.0 - (val / 100.0 * 8.0), 1)
                if "rain_adc" in query:
                    adc = int(query["rain_adc"][0])
                    system_state["rain_adc"] = adc
                    system_state["rain"] = adc < 3200
                if "fault" in query:
                    system_state["sensor_fault"] = (query["fault"][0] == "1")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status":"SIMULATION_UPDATED"}')
            return

        # 4. Default: Serve preview_dashboard.html at root
        if path == "/" or path == "/index.html":
            self.path = "/preview_dashboard.html"

        return super().do_GET()


def run_server():
    # Start FSM background worker
    t = threading.Thread(target=fsm_worker, daemon=True)
    t.start()

    # Reuse address to prevent 'Address already in use'
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), FloodGuardHandler) as httpd:
        print(f"==========================================================")
        print(f" FloodGuard Web Station running at: http://localhost:{PORT}")
        print(f" Real REST API endpoints available:")
        print(f"   - GET http://localhost:{PORT}/api/status")
        print(f"   - GET http://localhost:{PORT}/api/control")
        print(f"   - GET http://localhost:{PORT}/api/simulate")
        print(f"==========================================================")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
