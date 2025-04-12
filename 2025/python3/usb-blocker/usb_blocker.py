import os
import time
import pyudev

ALLOWED_FILE = "allowed_interfaces.txt"

def load_allowed_devices(filepath):
    allowed = set()
    if not os.path.exists(filepath):
        print(f"[!] Allowed list file not found: {filepath}")
        return allowed
    with open(filepath, "r") as file:
        for line in file:
            line = line.strip().split("#")[0]  # remove inline comments
            if line and ":" in line:
                allowed.add(line.lower())
    return allowed

def unbind_device_by_sys_name(sys_name):  #unmount and disconnect
    try:
        with open("/sys/bus/usb/drivers/usb/unbind", "w") as f:
            f.write(sys_name)
        print(f"[✗] Blocked device: {sys_name}")
    except Exception as e:
        print(f"[!] Error unbinding {sys_name}: {e}")

def monitor_usb(allowed_devices):
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    print("[*] Monitoring USB devices...")

    for device in iter(monitor.poll, None):
        if device.action != "add":
            continue

        vendor_id = device.get("ID_VENDOR_ID", "").lower()
        product_id = device.get("ID_MODEL_ID", "").lower()
        sys_name = device.sys_name

        if not vendor_id or not product_id:
            continue

        device_id = f"{vendor_id}:{product_id}"

        if device_id in allowed_devices:
            print(f"[✓] Allowed device connected: {device_id}")
        else:
            print(f"[!] Unauthorized device detected: {device_id}")
            time.sleep(0.5)
            unbind_device_by_sys_name(sys_name)

if __name__ == "__main__":
    allowed = load_allowed_devices(ALLOWED_FILE)
    monitor_usb(allowed)
    
