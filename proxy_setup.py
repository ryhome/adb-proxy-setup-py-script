import subprocess
import sys

def run_command(command, check_output=False):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error: {' '.join(command)} failed with error:\n{result.stderr.strip()}")
            return None if not check_output else False
        return result.stdout.strip() if check_output else True
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None if not check_output else False

def check_adb_device():
    print("Checking ADB connection...")
    output = run_command(["adb", "devices"], check_output=True)
    if output and "device" in output.splitlines()[-1]:
        print("Device connected.")
        return True
    print("No device detected. Please ensure the device is connected and ADB is enabled.")
    return False

def setup_proxy(proxy_ip="127.0.0.1", proxy_port=8080):
    if not check_adb_device():
        return
    
    print("Starting proxy setup...")
    
    # Switch to ADB root
    if not run_command(["adb", "root"]):
        print("Failed to switch to root. Ensure the device supports ADB root.")
        return
    
    # Clear and set HTTP proxy
    print("Configuring HTTP proxy...")
    run_command(["adb", "shell", "settings", "put", "global", "http_proxy", ":0"])
    run_command(["adb", "shell", "settings", "put", "global", "http_proxy", f"{proxy_ip}:{proxy_port}"])
    
    # Set up port forwarding
    print("Setting up port forwarding...")
    if not run_command(["adb", "reverse", f"tcp:{proxy_port}", f"tcp:{proxy_port}"]):
        print(f"Failed to set up port forwarding for {proxy_port}.")
        return
    
    # Apply iptables rules
    print("Applying iptables rules...")
    iptables_http_rule = [
        "adb", "shell", 
        "iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", f"{proxy_ip}:{proxy_port}"
    ]
    iptables_https_rule = [
        "adb", "shell", 
        "iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "--dport", "443", "-j", "DNAT", "--to-destination", f"{proxy_ip}:{proxy_port}"
    ]
    if not run_command(iptables_http_rule) or not run_command(iptables_https_rule):
        print("Failed to apply iptables rules. Ensure the device supports iptables and is rooted.")
        return
    
    print("Proxy setup completed successfully.")

def remove_proxy():
    if not check_adb_device():
        return
    
    print("Removing proxy configuration...")
    
    # Clear HTTP proxy
    print("Resetting HTTP proxy settings...")
    run_command(["adb", "shell", "settings", "put", "global", "http_proxy", ":0"])
    
    # Remove iptables rules
    print("Removing iptables rules...")
    iptables_http_rule = [
        "adb", "shell", 
        "iptables", "-t", "nat", "-D", "OUTPUT", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", "127.0.0.1:8080"
    ]
    iptables_https_rule = [
        "adb", "shell", 
        "iptables", "-t", "nat", "-D", "OUTPUT", "-p", "tcp", "--dport", "443", "-j", "DNAT", "--to-destination", "127.0.0.1:8080"
    ]
    run_command(iptables_http_rule)
    run_command(iptables_https_rule)
    
    # Remove port forwarding
    print("Removing port forwarding...")
    run_command(["adb", "reverse", "--remove-all"])
    
    print("Proxy configuration removed successfully.")

if __name__ == "__main__":
    action = input("Enter action (setup/remove): ").strip().lower()
    if action == "setup":
        proxy_ip = input("Enter proxy IP (default 127.0.0.1): ") or "127.0.0.1"
        try:
            proxy_port = int(input("Enter proxy port (default 8080): ") or "8080")
        except ValueError:
            print("Invalid port. Using default 8080.")
            proxy_port = 8080
        setup_proxy(proxy_ip, proxy_port)
    elif action == "remove":
        remove_proxy()
    else:
        print("Invalid action. Please enter 'setup' or 'remove'.")
