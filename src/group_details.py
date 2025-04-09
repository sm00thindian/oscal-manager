# group_details.py
import tkinter as tk
from tkinter import ttk
from oscal_pydantic.catalog import ControlGroup

class GroupDetails(ttk.Frame):
    """Handles display and editing of group details."""
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager  # Reference to CatalogManager for theme access

        tk.Label(self, text="ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.id_var = tk.StringVar()
        self.id_entry = tk.Entry(self, textvariable=self.id_var, width=80, state="readonly")
        self.id_entry.grid(row=0, column=1, pady=5)

        tk.Label(self, text="Title:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(self, textvariable=self.title_var, width=80)
        self.title_entry.grid(row=1, column=1, pady=5)

        tk.Label(self, text="Description:").grid(row=2, column=0, sticky="ne", padx=5, pady=5)
        self.desc_text = tk.Text(self, height=5, width=80)
        self.desc_text.grid(row=2, column=1, pady=5)

        tk.Label(self, text="Properties:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        self.props_text = tk.Text(self, height=5, width=80)
        self.props_text.grid(row=3, column=1, pady=5)

        tk.Label(self, text="Controls:").grid(row=4, column=0, sticky="ne", padx=5, pady=5)
        self.controls_text = tk.Text(self, height=5, width=80)
        self.controls_text.grid(row=4, column=1, pady=5)

        self.update_colors()

    def update_colors(self):
        """Update widget colors based on the current theme."""
        theme = self.manager.theme
        # Skip self (ttk.Frame) since it doesn't support bg/fg; style is set in CatalogManager
        for widget in [self.id_entry, self.title_entry, self.desc_text, self.props_text, self.controls_text]:
            widget.configure(bg=theme["field_bg"], fg=theme["fg"])
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=theme["bg"], fg=theme["fg"])

    def load(self, group: ControlGroup):
        self.id_var.set(group.id or "No ID")
        self.title_var.set(group.title or "No title")
        desc = "No description."
        if group.parts:
            for part in group.parts:
                if part.name == "statement" and part.prose:
                    desc = part.prose
                    break
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", desc)
        props = "\n".join(f"{prop.name}: {prop.value}" for prop in group.props or [])
        self.props_text.delete("1.0", tk.END)
        self.props_text.insert("1.0", props or "No properties.")
        controls = "\n".join(f"{control.id}: {control.title}" for control in group.controls or [])
        self.controls_text.delete("1.0", tk.END)
        self.controls_text.insert("1.0", controls or "No controls.")

    def save(self, group: ControlGroup):
        group.title = self.title_var.get()
