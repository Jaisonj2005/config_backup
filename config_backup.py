import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import os
import time

try:
    from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
    NETMIKO_AVAILABLE = True
except ImportError:
    NETMIKO_AVAILABLE = False

def backup_device(ip, username, password, simulate):
    text_output.config(state=tk.NORMAL)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, f"[*] Initiating backup job for {ip}...\n")
    btn_backup.config(state=tk.DISABLED)
    lbl_status.config(text="Connecting...", fg="#e67e22")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{ip}_{timestamp}.cfg"

    if simulate:
        # Portfolio testing mode: Simulates network delay and creates a dummy config file
        text_output.insert(tk.END, "[*] Running in Simulation Mode (No physical connection).\n")
        time.sleep(1.5)
        text_output.insert(tk.END, "[*] SSH connection established successfully.\n")
        time.sleep(1)
        text_output.insert(tk.END, "[*] Executing 'show running-config'...\n")
        
        dummy_config = f"!\n! Simulated Cisco IOS Configuration for {ip}\n!\nhostname R1\n!\ninterface GigabitEthernet0/0\n ip address {ip} 255.255.255.0\n no shutdown\n!\nrouter eigrp 100\n network 192.168.1.0\n!\nend"
        
        with open(filename, "w") as f:
            f.write(dummy_config)
            
        text_output.insert(tk.END, f"\n[SUCCESS] Configuration saved locally to:\n -> {filename}\n")
        lbl_status.config(text="Backup Complete", fg="#27ae60")
        
    else:
        # Live NOC Mode: Requires a real Cisco IOS device
        if not NETMIKO_AVAILABLE:
            text_output.insert(tk.END, "[!] Error: 'netmiko' library not installed.\n")
            lbl_status.config(text="Dependency Missing", fg="#c0392b")
            btn_backup.config(state=tk.NORMAL)
            return

        device = {
            'device_type': 'cisco_ios',
            'host': ip,
            'username': username,
            'password': password,
        }

        try:
            text_output.insert(tk.END, "[*] Negotiating SSH parameters...\n")
            net_connect = ConnectHandler(**device)
            text_output.insert(tk.END, "[*] Connection established. Pulling configuration...\n")
            
            output = net_connect.send_command("show running-config")
            
            with open(filename, "w") as f:
                f.write(output)
                
            net_connect.disconnect()
            text_output.insert(tk.END, f"\n[SUCCESS] Configuration saved locally to:\n -> {filename}\n")
            lbl_status.config(text="Backup Complete", fg="#27ae60")
            
        except NetmikoAuthenticationException:
            text_output.insert(tk.END, "[!] Authentication failed. Check credentials.\n")
            lbl_status.config(text="Auth Failed", fg="#c0392b")
        except NetmikoTimeoutException:
            text_output.insert(tk.END, "[!] Connection timed out. Device unreachable.\n")
            lbl_status.config(text="Timeout", fg="#c0392b")
        except Exception as e:
            text_output.insert(tk.END, f"[!] Unexpected error: {str(e)}\n")
            lbl_status.config(text="Error", fg="#c0392b")

    text_output.config(state=tk.DISABLED)
    btn_backup.config(state=tk.NORMAL)

def start_backup_thread():
    ip = entry_ip.get().strip()
    username = entry_user.get().strip()
    password = entry_pass.get()
    simulate = sim_var.get()

    if not ip or not username or not password:
        messagebox.showerror("Input Error", "Please fill in all device credentials.")
        return

    # Run on background thread to prevent UI freezing during SSH negotiation
    backup_thread = threading.Thread(target=backup_device, args=(ip, username, password, simulate), daemon=True)
    backup_thread.start()

# --- Tkinter GUI Layout ---
root = tk.Tk()
root.title("NOC Toolkit - Auto Config Backup")
root.geometry("450x480")
root.resizable(False, False)

frame = ttk.Frame(root, padding="15")
frame.pack(fill=tk.BOTH, expand=True)

lbl_title = tk.Label(frame, text="Router Configuration Backup", font=("Helvetica", 13, "bold"))
lbl_title.pack(anchor="w", pady=(0, 15))

# Credentials Grid
cred_frame = tk.Frame(frame)
cred_frame.pack(fill=tk.X, pady=(0, 15))

tk.Label(cred_frame, text="Device IP:", font=("Helvetica", 9)).grid(row=0, column=0, sticky="w", pady=5)
entry_ip = ttk.Entry(cred_frame, width=25)
entry_ip.grid(row=0, column=1, padx=10, pady=5)
entry_ip.insert(0, "192.168.1.1")

tk.Label(cred_frame, text="Username:", font=("Helvetica", 9)).grid(row=1, column=0, sticky="w", pady=5)
entry_user = ttk.Entry(cred_frame, width=25)
entry_user.grid(row=1, column=1, padx=10, pady=5)
entry_user.insert(0, "admin")

tk.Label(cred_frame, text="Password:", font=("Helvetica", 9)).grid(row=2, column=0, sticky="w", pady=5)
entry_pass = ttk.Entry(cred_frame, width=25, show="*")
entry_pass.grid(row=2, column=1, padx=10, pady=5)
entry_pass.insert(0, "cisco123")

# Simulation Toggle
sim_var = tk.BooleanVar(value=True)
chk_sim = tk.Checkbutton(frame, text="Simulation Mode (Offline Portfolio Testing)", variable=sim_var, font=("Helvetica", 9, "italic"), fg="#2980b9")
chk_sim.pack(anchor="w", pady=(0, 10))

# Controls
btn_backup = tk.Button(frame, text="Execute Backup", command=start_backup_thread, bg="#2c3e50", fg="white", font=("Helvetica", 9, "bold"), width=20)
btn_backup.pack(anchor="w", pady=(0, 10))

lbl_status = tk.Label(frame, text="Ready", font=("Helvetica", 9, "italic"), fg="#555")
lbl_status.pack(anchor="w", pady=(0, 10))

# Output Console
text_frame = tk.Frame(frame)
text_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_output = tk.Text(text_frame, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00", yscrollcommand=scrollbar.set)
text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
text_output.config(state=tk.DISABLED)
scrollbar.config(command=text_output.yview)

root.mainloop()