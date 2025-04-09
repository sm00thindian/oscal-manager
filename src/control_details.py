# control_details.py
import tkinter as tk
from tkinter import ttk
import webbrowser
import re
from oscal_pydantic.catalog import Control, Part

class ControlDetails(ttk.Frame):
    """Handles display and editing of control details."""
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager

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
        self.props_text = tk.Text(self, height=3, width=80)
        self.props_text.grid(row=3, column=1, pady=5)

        tk.Label(self, text="Statement Items:").grid(row=4, column=0, sticky="ne", padx=5, pady=5)
        self.items_text = tk.Text(self, height=5, width=80)
        self.items_text.grid(row=4, column=1, pady=5)

        tk.Label(self, text="Responsible Roles:").grid(row=5, column=0, sticky="ne", padx=5, pady=5)
        self.roles_text = tk.Text(self, height=2, width=80)
        self.roles_text.grid(row=5, column=1, pady=5)

        tk.Label(self, text="Implementation Status:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.status_var = tk.StringVar()
        self.status_entry = tk.Entry(self, textvariable=self.status_var, width=80)
        self.status_entry.grid(row=6, column=1, pady=5)

        tk.Label(self, text="References:").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
        self.refs_text = tk.Text(self, height=3, width=80)
        self.refs_text.grid(row=7, column=1, pady=5)

        tk.Label(self, text="Related Links:").grid(row=8, column=0, sticky="ne", padx=5, pady=5)
        self.links_frame = ttk.Frame(self)
        self.links_frame.grid(row=8, column=1, pady=5, sticky="w")
        self.link_labels = []

        tk.Label(self, text="Enhancements:").grid(row=9, column=0, sticky="ne", padx=5, pady=5)
        self.enhancements_text = tk.Text(self, height=3, width=80)
        self.enhancements_text.grid(row=9, column=1, pady=5)

        tk.Label(self, text="Parameters:").grid(row=10, column=0, sticky="ne", padx=5, pady=5)
        self.params_text = tk.Text(self, height=5, width=80)
        self.params_text.grid(row=10, column=1, pady=5)

        self.update_colors()

    def update_colors(self):
        """Update widget colors based on the current theme."""
        theme = self.manager.theme
        # Skip self (ttk.Frame) since it doesn't support bg/fg; style is set in CatalogManager
        for widget in [self.id_entry, self.title_entry, self.desc_text, self.props_text, 
                       self.items_text, self.roles_text, self.status_entry, self.refs_text, 
                       self.enhancements_text, self.params_text]:
            widget.configure(bg=theme["field_bg"], fg=theme["fg"])
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=theme["bg"], fg=theme["fg"])
        self.desc_text.tag_configure("normal", foreground=theme["fg"])
        self.desc_text.tag_configure("param", foreground="#00b7eb" if self.manager.is_dark_mode else "blue", 
                                    font=("Helvetica", 10, "bold"))
        for label in self.link_labels:
            label.configure(bg=theme["bg"], fg="#00b7eb" if self.manager.is_dark_mode else "blue")

    def parse_prose(self, prose, control_params, catalog_params):
        pattern = r"(\{\{\s*insert:\s*param,\s*(\w+)\s*\}\})"
        parts = re.split(pattern, prose)
        result = []
        for i in range(0, len(parts), 3):
            text = parts[i]
            if text:
                result.append((text, "normal"))
            if i + 1 < len(parts):
                param_id = parts[i + 2]
                param = next((p for p in control_params if p.id == param_id), None)
                if not param:
                    param = next((p for p in catalog_params if p.id == param_id), None)
                if param:
                    label = param.label or param.id
                    result.append((f"[{label}]", "param"))
                else:
                    result.append((f"[Unknown param: {param_id}]", "param"))
        return result

    def load(self, control: Control):
        self.id_var.set(control.id or "No ID")
        self.title_var.set(control.title or "")
        self.desc_text.delete("1.0", tk.END)
        for part in control.parts or []:
            if hasattr(part, 'name'):
                if part.name == "statement" and part.prose:
                    segments = self.parse_prose(part.prose, control.params or [], self.manager.catalog.params or [])
                    for text, tag in segments:
                        self.desc_text.insert(tk.END, text, tag)
                    self.desc_text.insert(tk.END, "\n")
            else:
                if part.get("name") == "statement" and part.get("prose"):
                    segments = self.parse_prose(part["prose"], control.params or [], self.manager.catalog.params or [])
                    for text, tag in segments:
                        self.desc_text.insert(tk.END, text, tag)
                    self.desc_text.insert(tk.END, "\n")

        props = "\n".join(f"{prop.name}: {prop.value}" for prop in control.props or [])
        self.props_text.delete("1.0", tk.END)
        self.props_text.insert("1.0", props or "No properties.")

        items = "\n".join(part.prose for part in control.parts or [] if part.name == "item")
        self.items_text.delete("1.0", tk.END)
        self.items_text.insert("1.0", items or "No statement items.")

        roles = "\n".join(link.role_id for link in control.links or [] if link.rel == "responsible-role")
        self.roles_text.delete("1.0", tk.END)
        self.roles_text.insert("1.0", roles or "No responsible roles.")

        status = next((prop.value for prop in control.props or [] if prop.name == "implementation-status"), "")
        self.status_var.set(status)

        refs = []
        for link in control.links or []:
            if link.rel == "reference":
                href = link.href
                if href.startswith("#"):
                    target_id = href[1:]
                    control_title = self.manager.get_control_title_by_id(target_id) or self.manager.get_resource_title_by_uuid(target_id)
                    refs.append(f"{control_title or 'Unknown'} ({target_id})")
                else:
                    refs.append(href)
        self.refs_text.delete("1.0", tk.END)
        self.refs_text.insert("1.0", "\n".join(refs) or "No references.")

        for label in self.link_labels:
            label.destroy()
        self.link_labels = []
        for link in control.links or []:
            if link.rel == "related":
                href = link.href
                link_type = "Internal" if href.startswith("#") else "External"
                display_text = href if link_type == "External" else f"{self.manager.get_control_title_by_id(href[1:]) or 'Unknown'} ({href[1:]})"
                lbl = tk.Label(self.links_frame, text=f"{display_text} ({link_type})", cursor="hand2")
                lbl.pack(anchor="w")
                if link_type == "External":
                    lbl.bind("<Button-1>", lambda e, url=href: webbrowser.open(url))
                else:
                    lbl.bind("<Button-1>", lambda e, tid=href[1:]: self.manager.select_control_by_id(tid, from_link=True))
                self.link_labels.append(lbl)

        enhancements = "\n".join(f"{ctrl.id}: {ctrl.title}" for ctrl in control.controls or [])
        self.enhancements_text.delete("1.0", tk.END)
        self.enhancements_text.insert("1.0", enhancements or "No enhancements.")

        params_info = ""
        referenced_param_ids = set()
        for part in control.parts or []:
            if part.name == "statement" and part.prose:
                matches = re.findall(r"\{\{\s*insert:\s*param,\s*(\w+)\s*\}\}", part.prose)
                referenced_param_ids.update(matches)
        all_params = (control.params or []) + (self.manager.catalog.params or [])
        displayed_params = set()
        for param_id in referenced_param_ids:
            param = next((p for p in all_params if p.id == param_id), None)
            if param and param.id not in displayed_params:
                params_info += f"ID: {param.id}\n"
                if param.label:
                    params_info += f"Label: {param.label}\n"
                if param.usage:
                    params_info += f"Usage: {param.usage}\n"
                if param.constraints:
                    params_info += "Constraints:\n"
                    for constraint in param.constraints:
                        params_info += f" - {constraint.description}\n"
                params_info += "\n"
                displayed_params.add(param.id)
        for param in control.params or []:
            if param.id not in displayed_params:
                params_info += f"ID: {param.id}\n"
                if param.label:
                    params_info += f"Label: {param.label}\n"
                if param.usage:
                    params_info += f"Usage: {param.usage}\n"
                if param.constraints:
                    params_info += "Constraints:\n"
                    for constraint in param.constraints:
                        params_info += f" - {constraint.description}\n"
                params_info += "\n"
                displayed_params.add(param.id)
        self.params_text.delete("1.0", tk.END)
        self.params_text.insert("1.0", params_info or "No parameters.")

        self.update_colors()

    def save(self, control: Control):
        control.title = self.title_var.get()
        for part in control.parts or []:
            if part.name == "statement":
                part.prose = self.desc_text.get("1.0", tk.END).strip()
                break
        else:
            control.parts = control.parts or []
            control.parts.append(Part(name="statement", prose=self.desc_text.get("1.0", tk.END).strip()))
        props_text = self.props_text.get("1.0", tk.END).strip()
        if props_text and props_text != "No properties.":
            control.props = []
            for line in props_text.split("\n"):
                if ": " in line:
                    name, value = line.split(": ", 1)
                    control.props.append({"name": name.strip(), "value": value.strip()})
        else:
            control.props = []
        status = self.status_var.get()
        if status:
            if not control.props:
                control.props = []
            for prop in control.props:
                if prop.name == "implementation-status":
                    prop.value = status
                    break
            else:
                control.props.append({"name": "implementation-status", "value": status})
