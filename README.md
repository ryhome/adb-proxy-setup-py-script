# Android ADB Proxy Configuration Script

This repository contains a Python script to manage proxy configurations for Android devices connected via ADB. The script allows you to set up or remove a proxy, enabling easier debugging and traffic analysis.

---

## Why Use This Script?

When debugging Android applications or analyzing network traffic, it is often useful to route the device's HTTP and HTTPS traffic through a proxy. This script automates the process of:

1. Configuring a proxy on the connected Android device.
2. Redirecting traffic to the proxy using `iptables` rules.
3. Removing the proxy configuration and restoring the device's default settings.

By automating these tasks, the script saves time and minimizes errors compared to manual configuration.

---

## What Does the Script Do?

### Key Features

- **Setup Proxy**: Configures the device to route traffic through a specified proxy (IP and port).
- **Remove Proxy**: Resets proxy settings and removes `iptables` rules.
- **Dynamic Configuration**: Allows customization of proxy IP and port.
- **Traffic Redirection**: Uses `iptables` rules to forward HTTP and HTTPS traffic to the proxy.
- **Port Forwarding**: Sets up ADB reverse port forwarding for seamless traffic routing.

### How It Works

1. **Proxy Setup**:
   - Sets the global HTTP proxy setting on the device.
   - Configures `iptables` rules to redirect HTTP (port 80) and HTTPS (port 443) traffic.
   - Establishes ADB reverse port forwarding to the proxy.

2. **Proxy Removal**:
   - Resets the global HTTP proxy setting to `none`.
   - Removes `iptables` rules for traffic redirection.
   - Deletes all ADB reverse port mappings.

---

## Prerequisites

- **Python Installed**: Ensure Python 3.x is installed on your computer.
- **ADB Installed**: Install ADB and make sure it's in your system's PATH.
  - Verify by running: `adb version`.
- **Connected Device**: Connect your Android device to your computer via USB with ADB debugging enabled.
- **Root Access**: The Android device must have ADB root access enabled for `iptables` commands to work.

---

## How to Use the Script

### 1. Clone the Repository

```bash
git clone https://github.com/<your-repo-name>/adb-proxy-setup-py-script.git
cd adb-proxy-setup-py-script
```

### 2. Run the Script

Execute the script to configure or remove a proxy on your device.

```bash
python proxy_setup.py
```

### 3. Choose an Action

- **Setup Proxy**: Configures the proxy on your device.
- **Remove Proxy**: Removes the proxy configuration and resets settings.

#### Option 1: Setup Proxy

1. Enter `setup` when prompted for an action.
2. Provide the following inputs:
   - **Proxy IP**: Default is `127.0.0.1`. Press Enter to use the default or specify another IP.
   - **Proxy Port**: Default is `8080`. Press Enter to use the default or specify another port.

Example Input:
```plaintext
Enter action (setup/remove): setup
Enter proxy IP (default 127.0.0.1):
Enter proxy port (default 8080):
```

#### Option 2: Remove Proxy

1. Enter `remove` when prompted for an action.
2. The script will:
   - Reset the `http_proxy` setting to `none`.
   - Remove any `iptables` rules related to the proxy.
   - Clear ADB reverse port mappings.

Example Input:
```plaintext
Enter action (setup/remove): remove
```

---

## Script Details

### Commands Used

#### Proxy Setup:
```bash
adb shell settings put global http_proxy 127.0.0.1:8080
adb reverse tcp:8080 tcp:8080
adb shell iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination 127.0.0.1:8080
adb shell iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination 127.0.0.1:8080
```

#### Proxy Removal:
```bash
adb shell settings put global http_proxy :0
adb shell iptables -t nat -D OUTPUT -p tcp --dport 80 -j DNAT --to-destination 127.0.0.1:8080
adb shell iptables -t nat -D OUTPUT -p tcp --dport 443 -j DNAT --to-destination 127.0.0.1:8080
adb reverse --remove-all
```

---

## Troubleshooting

- **No Device Detected**: Ensure the device is connected and ADB debugging is enabled. Check with:
  ```bash
  adb devices
  ```
- **ADB Root Fails**: Confirm that your device supports ADB root access.
- **Persistent Proxy**: The proxy settings and `iptables` rules might reset on device reboot. Re-run the script as needed.

---

## Contributing

Feel free to fork this repository and contribute enhancements or bug fixes. Open a pull request with a detailed explanation of your changes.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
