from customtkinter import (CTk, CTkLabel, CTkFrame, CTkEntry, CTkButton, CTkOptionMenu,
                           CTkCheckBox, StringVar, CTkImage, CTkScrollableFrame, CTkToplevel,
                           set_appearance_mode, set_default_color_theme, CTkBaseClass, CTkTextbox)

import threading
from subprocess import Popen, PIPE
from tkinter import Listbox, messagebox

import lan_broadcaster.constants as c

class App(CTk):
    """Main application class for this program"""

    def __init__(self):
        super().__init__()
        
        self.title(c.APPLICATION_TITLE)
        self.geometry(c.APPLICATION_GEOMETRY)
        self.iconbitmap(c.WINDOW_ICON_PATH)

        self.frame = CTkFrame(self)
        self.frame.pack(anchor="center", expand=True, fill="both", padx=10, pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)

        # ---Left Side of Window--- #

        self.options_menu = CTkLabel(self.frame, text="Options:", font=c.HEADER_FONT)
        self.options_menu.grid(row=0, column=0, pady=(5,0), padx=10, sticky="w")

        self.ip_label = CTkLabel(self.frame, text="IP of Destination (on LAN)",
                                 font=c.MAIN_FONT)
        self.ip_label.grid(row=1, column=0, sticky="w", padx=10, pady=(10,0))

        self.ip_entry = CTkEntry(self.frame, width=260, font=c.MAIN_FONT,
                                 placeholder_text="Enter a valid IP address",)
        self.ip_entry.grid(row=1, column=1, sticky="w", padx=10, pady=(10,0))

        self.user_label = CTkLabel(self.frame, font=c.MAIN_FONT,
                                   text="Name of User (leave blank to send to all users)")
        self.user_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10,0))

        self.user_entry = CTkEntry(self.frame, width=260, font=c.MAIN_FONT,
                                   placeholder_text="Enter username (as appears on machine)")
        self.user_entry.grid(row=2, column=1, sticky="w", padx=10, pady=(10,0))

        self.message_label = CTkLabel(self.frame, text="Message", font=c.MAIN_FONT)
        self.message_label.grid(row=3, column=0, sticky="w", padx=10, pady=(10,0))

        self.message_entry = CTkEntry(self.frame, placeholder_text="Enter message to send",
                                      font=c.MAIN_FONT, width=260)
        self.message_entry.grid(row=3, column=1, sticky="w", padx=10, pady=(10,0))

        self.verbose_option_var = StringVar(value="off")
        self.verbose_option = CTkCheckBox(self.frame, 
                                          variable=self.verbose_option_var, font=c.MAIN_FONT,
                                          offvalue="off", onvalue="on", text="Verbose Mode")
        self.verbose_option.grid(row=4, column=0, sticky="w", padx=10, pady=(10,0))

        self.execute_button = CTkButton(self.frame, text="Run Command",
                                        font=c.MAIN_FONT, command=self.run)
        self.execute_button.grid(row=5, column=0, sticky="ew", padx=10, pady=(15,0))

        self.output_label = CTkLabel(self.frame, text="Output:", font=c.HEADER_FONT)
        self.output_label.grid(row=6, column=0, sticky="w", padx=10, pady=(10,0))

        self.output_box = CTkTextbox(self.frame, font=("Courier New", 11),
                                     width=510, height=210)
        self.output_box.grid(row=7, column=0, sticky="w", padx=10,
                             pady=(10,0), columnspan=2)
        self.output_box.configure(state="disabled")

        self.ip_entry.bind("<Return>", lambda _: self.run())
        self.user_entry.bind("<Return>", lambda _: self.run())
        self.message_entry.bind("<Return>", lambda _: self.run())

        # ---Right Side of Window--- #

        self.arp_ping_button = CTkButton(self.frame, text="Find Devices (ARP Ping)",
                                         font=c.MAIN_FONT, command=self.run_arp)
        self.arp_ping_button.grid(row=0, column=2, sticky="ew",
                                  padx=(40,0), pady=(10,0))

        self.devices = Listbox(self.frame, width=55, height=27, border=0)
        self.devices.grid(row=1, column=2, rowspan=7, padx=(40,0),
                          sticky="ew", pady=(10,0))

    def msg(self, ip_address: str, user: str, message: str) -> None:
        self.update_output_box("Running...\n\n")  # Display initial status

        command = ["msg", user, f"/server:{ip_address}"]
        verbose = self.verbose_option_var.get()

        if verbose == "on":
            command.append("/V")

        command.append(message)
        
        msg = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")

        for line in msg.stdout:
            self.update_output_box(line.rstrip("\n") + "\n")

        if msg.stderr:
            for line in msg.stderr:
                self.update_output_box(line.rstrip("\n") + "\n")

        if msg.wait() == 0:
            self.update_output_box("\nCompleted successfully!")
        else:
            self.update_output_box("\nCommand failed!")
    
    def update_output_box(self, content: str):
        """Safely update the output box from the main thread."""
        def update():
            self.output_box.configure(state="normal")
            self.output_box.insert("end", content)
            self.output_box.see("end")  # Scroll to the end to show the latest output
            self.output_box.configure(state="disabled")

        self.after(0, update)  # Schedule update on the main thread

    def run(self):
        self.clear_output_box()  # Clear the output box before running a new command
        self.disable_bindings()  # Disable bindings to prevent multiple commands

        def run_command():
            ip_address = self.ip_entry.get()
            user = self.user_entry.get()
            message = self.message_entry.get()
            if not user:
                user = "*"
            try:
                self.msg(ip_address, user, message)
            except Exception:
                messagebox.showerror("Error", "An error occurred whilst completing the msg command.")
            finally:
                self.enable_bindings()  # Re-enable bindings after command completes

        thread = threading.Thread(target=run_command)
        thread.start()

    def clear_output_box(self):
        """Clear the output box."""
        self.output_box.configure(state="normal")
        self.output_box.delete(0.0, "end")
        self.output_box.configure(state="disabled")

    def disable_bindings(self):
        """Disable return key bindings temporarily."""
        self.ip_entry.unbind("<Return>")
        self.user_entry.unbind("<Return>")
        self.message_entry.unbind("<Return>")

    def enable_bindings(self):
        """Enable return key bindings."""
        self.ip_entry.bind("<Return>", lambda _: self.run())
        self.user_entry.bind("<Return>", lambda _: self.run())
        self.message_entry.bind("<Return>", lambda _: self.run())

    def arp(self):
        self.devices.delete(0, "end")
        arp = Popen("arp -a", shell=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")
        current_interface = None

        for line in arp.stdout:
            if line.startswith("Interface:"):
                current_interface = line.split()[1]
                self.devices.insert("end", f"Current Device: {current_interface}")
            elif "static" in line or "dynamic" in line:
                parts = line.split()
                ip_address = parts[0]
                entry_type = parts[-1]
                self.devices.config(font=("Segoe UI", 9))                
                if entry_type == "static": entry_type = "Static"
                if entry_type == "dynamic": entry_type = "Dynamic"
                self.devices.insert("end", f"{ip_address} - {entry_type}")
                
        self.arp_ping_button.configure(state="normal")

    def run_arp(self):
        self.arp_ping_button.configure(state="disabled")
        def run_command():
            self.arp()
        thread = threading.Thread(target=run_command)
        thread.start()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
