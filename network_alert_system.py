import psutil
import time
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import winsound
import threading

# Initialize tkinter
root = tk.Tk()
root.title("Optimized Network Monitor")
root.geometry("800x600")

bytes_sent = tk.StringVar()
bytes_recv = tk.StringVar()
alert_msg = tk.StringVar()
refresh_interval = 5000  # Dynamic refresh interval (ms)

# UI Layout
frame1 = ttk.LabelFrame(root, text="Network Statistics")
frame1.pack(fill="x", padx=10, pady=5)
ttk.Label(frame1, textvariable=bytes_sent).pack()
ttk.Label(frame1, textvariable=bytes_recv).pack()

frame2 = ttk.LabelFrame(root, text="Active Network Connections")
frame2.pack(fill="both", expand=True, padx=9, pady=5)
connections_list = tk.Listbox(frame2, height=5)
connections_list.pack(fill="both", expand=True)

frame3 = ttk.LabelFrame(root, text="Processes Using Network")
frame3.pack(fill="both", expand=True, padx=10, pady=5)
fig = Figure(figsize=(6, 3))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=frame3)
canvas.get_tk_widget().pack(fill="both", expand=True)

frame4 = ttk.LabelFrame(root, text="Alerts")
frame4.pack(fill="x", padx=10, pady=5)
ttk.Label(frame4, textvariable=alert_msg, foreground="red").pack()

x_values, sent_values, recv_values = [], [], []
log_buffer = []
log_lock = threading.Lock()

# Logging setup
def setup_logging():
    log_dir = os.path.join("logs", datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def buffer_log(event):
    with log_lock:
        log_buffer.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {event}")

def write_logs():
    while True:
        time.sleep(600)  # Write logs every 10 minutes
        with log_lock:
            if log_buffer:
                log_file = os.path.join(setup_logging(), datetime.now().strftime("%H") + ".log")
                with open(log_file, "a") as f:
                    f.write("\n".join(log_buffer) + "\n")
                log_buffer.clear()

threading.Thread(target=write_logs, daemon=True).start()

def play_alert():
    winsound.Beep(1000, 500)

def update_network_info():
    global refresh_interval
    net_io = psutil.net_io_counters()
    sent_mb, recv_mb = net_io.bytes_sent / (1024 * 1024), net_io.bytes_recv / (1024 * 1024)

    bytes_sent.set(f"Bytes Sent: {sent_mb:.2f} MB")
    bytes_recv.set(f"Bytes Received: {recv_mb:.2f} MB")
    detect_anomalies(sent_mb, recv_mb)
    update_graph(sent_mb, recv_mb)
    
    refresh_interval = 3000 if (sent_mb > 2000 or recv_mb > 2000) else 7000
    root.after(refresh_interval, update_network_info)

def detect_anomalies(sent, recv):
    threshold = 3000
    if sent > threshold or recv > threshold:
        alert_msg.set(f"High network usage detected: Sent={sent:.2f}MB, Recv={recv:.2f}MB")
        messagebox.showwarning("Alert", alert_msg.get())
        play_alert()
        buffer_log(alert_msg.get())

def update_active_connections():
    while True:
        connections_list.delete(0, tk.END)
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_ESTABLISHED:
                connections_list.insert(tk.END, f"{conn.laddr.ip}:{conn.laddr.port} <--> {conn.raddr.ip}:{conn.raddr.port}")
        time.sleep(10)  # Refresh every 10 seconds

def update_graph(sent, recv):
    global x_values, sent_values, recv_values
    x_values.append(time.strftime("%H:%M:%S"))
    sent_values.append(sent)
    recv_values.append(recv)
    
    if len(x_values) > 20:
        x_values.pop(0)
        sent_values.pop(0)
        recv_values.pop(0)

    ax.clear()
    ax.plot(x_values, sent_values, label="Bytes Sent (MB)", color="blue")
    ax.plot(x_values, recv_values, label="Bytes Received (MB)", color="red")
    ax.legend()
    ax.set_title("Network Traffic Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("MB")
    canvas.draw()

threading.Thread(target=update_active_connections, daemon=True).start()
root.after(refresh_interval, update_network_info)
root.mainloop()

