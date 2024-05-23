import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import threading
import paramiko
from tkinter import messagebox

def create_rounded_rectangle(width, height, radius, color):
    # Create a blank image with transparent background
    image = Image.new("RGBA", (width, height), (255, 0, 0, 0))

    # Create a rectangle with slightly rounded corners
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill=color)

    return image

class SSHApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SSH Tunnel Automation")
        self.geometry("750x400")

        self.is_tunnel_open = False
        self.ssh_client = None

        # Connection Parameters
        self.hostname_var = tk.StringVar()
        self.port_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(self, text="Hostname:").pack()
        tk.Entry(self, textvariable=self.hostname_var).pack()

        self.port_var = tk.StringVar(value="22")
        tk.Label(self, text="Port:").pack()
        tk.Entry(self, textvariable=self.port_var).pack()

        tk.Label(self, text="Username:").pack()
        tk.Entry(self, textvariable=self.username_var).pack()

        tk.Label(self, text="Password:").pack()
        tk.Entry(self, textvariable=self.password_var, show="*").pack()

        # Tunnel Port
        self.tunnel_port_var = tk.StringVar(value="8888")
        tk.Label(self, text="Tunnel Port:").pack()
        tk.Entry(self, textvariable=self.tunnel_port_var).pack()

        # Error Label
        self.error_label = tk.Label(self, fg="red")
        self.error_label.pack()

        # Button
        self.button_label = tk.Label(self, text="Open Tunnel", fg="white", compound="center", cursor="hand2")
        self.button_label.pack(pady=20)
        self.update_button_color("red")  # Set initial button color
        self.button_label.bind("<Button-1>", self.toggle_tunnel)

    def create_button_image(self, width, height, radius, color):
        image = Image.new("RGBA", (width, height), (255, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, width, height), radius, fill=color)
        return ImageTk.PhotoImage(image)

    def update_button_color(self, color):
        button_image = self.create_button_image(200, 50, 10, color)
        self.button_label.config(image=button_image)
        self.button_label.image = button_image  # Keep a reference to avoid garbage collection

    def toggle_tunnel(self, event):
        if not self.is_tunnel_open:
            try:
                self.open_tunnel()
            except Exception as e:
                self.show_error_dialog(f"Failed to open tunnel: {str(e)}")
        else:
            try:
                self.close_tunnel()
            except Exception as e:
                self.show_error_dialog(f"Failed to close tunnel: {str(e)}")
        self.is_tunnel_open = not self.is_tunnel_open

    def show_error_dialog(self, message):
        messagebox.showerror("Error", message)

    def open_tunnel(self):
        def ssh_thread():
            try:
                hostname = self.hostname_var.get()
                port = int(self.port_var.get())
                username = self.username_var.get()
                password = self.password_var.get()
                tunnel_port = int(self.tunnel_port_var.get())

                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(hostname=hostname, port=port, username=username, password=password, timeout=10)
                transport = self.ssh_client.get_transport()
                self.tunnel = transport.open_channel("direct-tcpip", ("localhost", tunnel_port), ("localhost", 0))
                self.update_button_color("green")  # Change button color to green when tunnel is successfully opened
                self.error_label.config(text="")  # Clear any previous error message
            except Exception as e:
                self.error_label.config(text=f"Error: {str(e)}")
                raise RuntimeError(f"Failed to open tunnel: {str(e)}")

        threading.Thread(target=ssh_thread).start()

    def close_tunnel(self):
        def close_ssh_tunnel():
            try:
                if self.ssh_client:
                    tunnel_port = int(self.tunnel_port_var.get())
                    username = self.username_var.get()
                    remote_host = self.hostname_var.get()
                    self.ssh_client.exec_command(f'pkill -f "ssh -N -L {tunnel_port}:localhost:{tunnel_port} {username}@{remote_host}"')
                    self.ssh_client.close()
                    self.update_button_color("red")  # Change button color to red when tunnel is successfully closed
            except Exception as e:
                self.error_label.config(text=f"Error: {str(e)}")
                raise RuntimeError(f"Failed to close tunnel: {str(e)}")

        threading.Thread(target=close_ssh_tunnel).start()

if __name__ == "__main__":
    app = SSHApplication()
    app.mainloop()
