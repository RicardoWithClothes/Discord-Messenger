import tkinter as tk

class LogsPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#23272A", width=300)
        self.pack_propagate(False)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="QUEUE & LOGS", bg="#23272A", fg="#7289DA", font=("Arial", 12, "bold")).pack(pady=10)

        self.queue_box = tk.Listbox(self, bg="#2C2F33", fg="white", height=8, bd=0)
        self.queue_box.pack(fill="x", padx=5)

        tk.Label(self, text="System Output:", bg="#23272A", fg="#99AAB5").pack(anchor="w", padx=5, pady=(10,0))
        
        self.log_text = tk.Text(self, bg="#000000", fg="#00FF00", font=("Consolas", 8), bd=0)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def refresh_queue(self, tasks):
        self.queue_box.delete(0, tk.END)
        for i, task in enumerate(tasks):
            self.queue_box.insert(tk.END, str(task))
            # Zebra Striping
            bg_color = "#2C2F33" if i % 2 == 0 else "#202225"
            self.queue_box.itemconfigure(i, bg=bg_color)