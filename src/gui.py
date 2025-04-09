import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from oscal_pydantic.catalog import Catalog, ControlGroup, Control, Part
from pydantic import ValidationError
import json
import webbrowser
import re
import os
from PIL import Image, ImageTk
try:
    import darkdetect  # Optional, for better theme detection
    DARKDETECT_AVAILABLE = True
except ImportError:
    DARKDETECT_AVAILABLE = False

def save_catalog(catalog: Catalog, file_path: str):
    """Save the catalog to a JSON file."""
    with open(file_path, 'w') as f:
        f.write(catalog.json(exclude_none=True, indent=2))

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

class DetailsPane(ttk.Frame):
    """Manages switching between group and control details with scrolling."""
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager

        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(fill="x", pady=5)
        self.back_button = tk.Button(self.nav_frame, text="Back", command=self.manager.go_back, state=tk.DISABLED)
        self.back_button.pack(side="left", padx=5)
        self.new_control_button = tk.Button(self.nav_frame, text="New Control", command=self.manager.new_control)
        self.new_control_button.pack(side="left", padx=5)
        self.new_group_button = tk.Button(self.nav_frame, text="New Group", command=self.manager.new_group)
        self.new_group_button.pack(side="left", padx=5)
        self.delete_control_button = tk.Button(self.nav_frame, text="Delete Control", command=self.manager.delete_control)
        self.delete_control_button.pack(side="left", padx=5)
        self.delete_group_button = tk.Button(self.nav_frame, text="Delete Group", command=self.manager.delete_group)
        self.delete_group_button.pack(side="left", padx=5)
        self.save_button = tk.Button(self.nav_frame, text="Save Changes", command=self.manager.save_changes)
        self.save_button.pack(side="left", padx=5)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.group_details = GroupDetails(self.scrollable_frame, manager)
        self.control_details = ControlDetails(self.scrollable_frame, manager)
        self.no_selection_label = tk.Label(self.scrollable_frame, text="Select a group or control to edit")
        self.no_selection_label.pack(pady=5)
        self.current_details = None
        self.current_object = None

        self.update_colors()

    def update_colors(self):
        """Update widget colors based on the current theme."""
        theme = self.manager.theme
        self.canvas.configure(bg=theme["bg"])
        self.scrollable_frame.configure(style="TFrame")
        self.no_selection_label.configure(bg=theme["bg"], fg=theme["fg"])
        for button in [self.back_button, self.new_control_button, self.new_group_button, 
                       self.delete_control_button, self.delete_group_button, self.save_button]:
            button.configure(bg=theme["button_bg"], fg=theme["fg"], disabledforeground=theme["disabled_fg"])
        self.group_details.update_colors()
        self.control_details.update_colors()

    def show_group(self, group: ControlGroup):
        self.control_details.pack_forget()
        self.group_details.pack(fill="both", expand=True, padx=5, pady=5)
        self.group_details.load(group)
        self.current_details = self.group_details
        self.current_object = group
        self.no_selection_label.pack_forget()
        self.new_control_button.config(state=tk.NORMAL)
        self.new_group_button.config(state=tk.NORMAL)
        self.delete_control_button.config(state=tk.DISABLED)
        self.delete_group_button.config(state=tk.NORMAL)
        self.update_colors()

    def show_control(self, control: Control):
        self.group_details.pack_forget()
        self.control_details.pack(fill="both", expand=True, padx=5, pady=5)
        self.control_details.load(control)
        self.current_details = self.control_details
        self.current_object = control
        self.no_selection_label.pack_forget()
        self.new_control_button.config(state=tk.DISABLED)
        self.new_group_button.config(state=tk.NORMAL)
        self.delete_control_button.config(state=tk.NORMAL)
        self.delete_group_button.config(state=tk.DISABLED)
        self.update_colors()

    def clear(self):
        self.group_details.pack_forget()
        self.control_details.pack_forget()
        self.no_selection_label.pack()
        self.current_details = None
        self.current_object = None
        self.new_control_button.config(state=tk.DISABLED)
        self.new_group_button.config(state=tk.NORMAL)
        self.delete_control_button.config(state=tk.DISABLED)
        self.delete_group_button.config(state=tk.DISABLED)
        self.update_colors()

    def save_current(self):
        if self.current_details and self.current_object:
            self.current_details.save(self.current_object)

class CatalogManager:
    """Main GUI class for managing the OSCAL catalog with dynamic theming."""
    def __init__(self, catalog: Catalog, root: tk.Tk):
        self.catalog = catalog
        self.root = root
        self.root.title("OSCAL Manager")
        self.history = []
        self.images = []

        # Detect system theme (dark or light)
        self.is_dark_mode = self.detect_system_theme()

        # Define color schemes
        self.light_theme = {
            "bg": "#e0e0e0", "fg": "black", "tree_bg": "#f0f0f0", "tree_fg": "black",
            "group_bg": "#d0d0d0", "control_bg": "#e8e8e8", "field_bg": "#f0f0f0",
            "tooltip_bg": "#ffffe0", "button_bg": "#d3d3d3", "disabled_fg": "#a3a3a3"
        }
        self.dark_theme = {
            "bg": "#2e2e2e", "fg": "white", "tree_bg": "#3c3c3c", "tree_fg": "white",
            "group_bg": "#4a4a4a", "control_bg": "#383838", "field_bg": "#3c3c3c",
            "tooltip_bg": "#4a4a4a", "button_bg": "#555555", "disabled_fg": "#888888"
        }
        self.theme = self.dark_theme if self.is_dark_mode else self.light_theme

        # Configure root background
        self.root.configure(bg=self.theme["bg"])

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview setup
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        style = ttk.Style()
        style.theme_use('clam')
        self.configure_styles(style)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Title"), show="tree headings", height=20)
        self.tree.heading("#0", text="")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.column("#0", width=50, minwidth=50)
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=350)
        self.tree.pack(side="top", fill="both", expand=True)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Load icons
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_path)
        try:
            folder_path = os.path.join(project_root, "icons", "folder.png")
            file_path = os.path.join(project_root, "icons", "file.png")
            folder_img = Image.open(folder_path).resize((16, 16))
            file_img = Image.open(file_path).resize((16, 16))
            self.folder_img = ImageTk.PhotoImage(folder_img)
            self.file_img = ImageTk.PhotoImage(file_img)
            self.images.append(self.folder_img)
            self.images.append(self.file_img)
        except FileNotFoundError as e:
            print(f"Error loading icons: {e}")
            self.folder_img = None
            self.file_img = None

        # Populate tree
        for group in self.catalog.groups or []:
            group_node = self.tree.insert("", "end", text="", values=(group.id, group.title), 
                                        tags=("group",), image=self.folder_img, open=False)
            for control in group.controls or []:
                self.tree.insert(group_node, "end", text="", values=(control.id, control.title), 
                                tags=("control",), image=self.file_img)

        self.tree.tag_configure("group", font=('Helvetica', 10, 'bold'), background=self.theme["group_bg"])
        self.tree.tag_configure("control", font=('Helvetica', 10), background=self.theme["control_bg"])
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Tooltip setup
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_attributes("-topmost", True)
        self.tooltip.withdraw()
        self.tooltip_label = tk.Label(self.tooltip, background=self.theme["tooltip_bg"], 
                                    foreground=self.theme["fg"], relief="solid", borderwidth=1, 
                                    justify="left", wraplength=300)
        self.tooltip_label.pack()
        self.tooltip_timer = None

        self.tree.bind("<Motion>", self.on_tree_motion)
        self.tree.bind("<Leave>", self.on_tree_leave)
        self.tree.bind("<ButtonPress>", lambda e: self.hide_tooltip())

        # Details pane
        self.details_pane = DetailsPane(main_frame, self)
        self.details_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.details_pane.clear()

        # Bind theme change detection
        self.root.after(1000, self.check_theme_change)

    def detect_system_theme(self):
        """Detect if the system is in dark mode."""
        if DARKDETECT_AVAILABLE:
            return darkdetect.isDark()
        # Fallback: Check Tkinter window background (approximation)
        bg = self.root.cget("bg")
        if bg.startswith("#") and int(bg[1:], 16) < 0x808080:  # Rough heuristic for dark
            return True
        return False

    def configure_styles(self, style):
        """Configure styles based on current theme."""
        style.configure("TFrame", background=self.theme["bg"])
        style.configure("Treeview", background=self.theme["tree_bg"], foreground=self.theme["tree_fg"], 
                        fieldbackground=self.theme["field_bg"])
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), 
                        background=self.theme["group_bg"], foreground=self.theme["fg"])
        style.map("Treeview", background=[('selected', '#a0a0a0' if self.is_dark_mode else '#b0c4de')])

    def check_theme_change(self):
        """Periodically check if the system theme has changed."""
        new_dark_mode = self.detect_system_theme()
        if new_dark_mode != self.is_dark_mode:
            self.is_dark_mode = new_dark_mode
            self.theme = self.dark_theme if self.is_dark_mode else self.light_theme
            self.root.configure(bg=self.theme["bg"])
            self.configure_styles(ttk.Style())
            self.tree.tag_configure("group", font=('Helvetica', 10, 'bold'), background=self.theme["group_bg"])
            self.tree.tag_configure("control", font=('Helvetica', 10), background=self.theme["control_bg"])
            self.tooltip_label.config(background=self.theme["tooltip_bg"], foreground=self.theme["fg"])
            self.details_pane.update_colors()
            self.root.update_idletasks()
        self.root.after(1000, self.check_theme_change)

    def show_tooltip(self, x, y, text):
        self.tooltip_label.config(text=text)
        self.tooltip.geometry(f"+{x+10}+{y+10}")
        self.tooltip.deiconify()

    def hide_tooltip(self):
        self.tooltip.withdraw()

    def on_tree_motion(self, event):
        if self.tooltip_timer:
            self.root.after_cancel(self.tooltip_timer)
        item = self.tree.identify_row(event.y)
        if item:
            self.tooltip_timer = self.root.after(500, lambda: self.show_tooltip_for_item(item, event.x_root, event.y_root))
        else:
            self.hide_tooltip()

    def on_tree_leave(self, event):
        if self.tooltip_timer:
            self.root.after_cancel(self.tooltip_timer)
            self.tooltip_timer = None
        self.hide_tooltip()

    def show_tooltip_for_item(self, item, x, y):
        item_id = self.tree.item(item, "values")[0]
        tags = self.tree.item(item, "tags")
        if "group" in tags:
            group = self.find_group_by_id(item_id)
            if group:
                text = f"Group: {group.id}\n{group.title}"
        elif "control" in tags:
            control = self.find_control_by_id(item_id)
            if control:
                statement_part = None
                for part in control.parts or []:
                    if hasattr(part, 'name'):
                        if part.name == "statement":
                            statement_part = part
                            break
                    elif isinstance(part, dict) and part.get("name") == "statement":
                        statement_part = part
                        break
                desc_snippet = statement_part.prose[:100] + "..." if statement_part and statement_part.prose else "No description."
                text = f"Control: {control.id}\n{control.title}\n{desc_snippet}"
        else:
            text = ""
        if text:
            self.show_tooltip(x, y, text)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            tags, item_id = item["tags"], item["values"][0]
            if "group" in tags:
                group = self.find_group_by_id(item_id)
                if group:
                    self.history.append(("group", item_id))
                    self.details_pane.show_group(group)
            elif "control" in tags:
                control = self.find_control_by_id(item_id)
                if control:
                    self.history.append(("control", item_id))
                    self.details_pane.show_control(control)
            self.update_back_button_state()
        else:
            self.details_pane.clear()

    def find_group_by_id(self, group_id: str) -> ControlGroup:
        return next((g for g in self.catalog.groups or [] if g.id == group_id), None)

    def find_control_by_id(self, control_id: str) -> Control:
        for group in self.catalog.groups or []:
            for control in group.controls or []:
                if control.id == control_id:
                    return control
        return None

    def find_tree_item_by_id(self, target_id):
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == target_id:
                return item
            for child in self.tree.get_children(item):
                if self.tree.item(child, "values")[0] == target_id:
                    return child
        return None

    def get_control_title_by_id(self, control_id):
        control = self.find_control_by_id(control_id)
        return control.title if control else None

    def get_resource_title_by_uuid(self, uuid):
        if hasattr(self.catalog, 'back_matter') and self.catalog.back_matter:
            for resource in self.catalog.back_matter.resources or []:
                if resource.uuid == uuid:
                    return resource.title
        return None

    def select_control_by_id(self, control_id, from_link=False):
        item = self.find_tree_item_by_id(control_id)
        if item:
            self.tree.selection_set(item)
            self.tree.see(item)
        else:
            messagebox.showinfo("Not Found", f"Control {control_id} not found.")

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            tag, item_id = self.history[-1]
            item = self.find_tree_item_by_id(item_id)
            if item:
                self.tree.selection_set(item)
                self.tree.see(item)
            self.update_back_button_state()

    def update_back_button_state(self):
        self.details_pane.back_button.config(state=tk.NORMAL if len(self.history) > 1 else tk.DISABLED)

    def is_control_id_unique(self, control_id):
        for group in self.catalog.groups or []:
            for control in group.controls or []:
                if control.id == control_id:
                    return False
        return True

    def is_group_id_unique(self, group_id):
        for group in self.catalog.groups or []:
            if group.id == group_id:
                return False
        return True

    def new_control(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            tags = item["tags"]
            if "group" in tags:
                group_id = item["values"][0]
                group = self.find_group_by_id(group_id)
                if group:
                    new_id = simpledialog.askstring("New Control", "Enter unique ID for the new control:", parent=self.root)
                    if new_id:
                        if self.is_control_id_unique(new_id):
                            new_control = Control(id=new_id, title="New Control")
                            group.controls = group.controls or []
                            group.controls.append(new_control)
                            control_node = self.tree.insert(selected[0], "end", text="", values=(new_id, "New Control"), 
                                                          tags=("control",), image=self.file_img)
                            self.tree.selection_set(control_node)
                            self.tree.see(control_node)
                            self.details_pane.show_control(new_control)
                        else:
                            messagebox.showerror("Error", f"Control ID '{new_id}' already exists.")
                    else:
                        messagebox.showwarning("Warning", "No ID provided for new control.")
            else:
                messagebox.showwarning("Warning", "Please select a group to add a new control.")
        else:
            messagebox.showwarning("Warning", "Please select a group to add a new control.")

    def new_group(self):
        new_id = simpledialog.askstring("New Group", "Enter unique ID for the new group:", parent=self.root)
        if new_id:
            if self.is_group_id_unique(new_id):
                new_group = ControlGroup(id=new_id, title="New Group")
                self.catalog.groups = self.catalog.groups or []
                self.catalog.groups.append(new_group)
                group_node = self.tree.insert("", "end", text="", values=(new_id, "New Group"), 
                                            tags=("group",), image=self.folder_img, open=False)
                self.tree.selection_set(group_node)
                self.tree.see(group_node)
                self.details_pane.show_group(new_group)
            else:
                messagebox.showerror("Error", f"Group ID '{new_id}' already exists.")
        else:
            messagebox.showwarning("Warning", "No ID provided for new group.")

    def delete_control(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            tags = item["tags"]
            if "control" in tags:
                control_id = item["values"][0]
                control = self.find_control_by_id(control_id)
                if control:
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete control '{control_id}'?"):
                        for group in self.catalog.groups or []:
                            if control in group.controls:
                                group.controls.remove(control)
                                break
                        self.tree.delete(selected[0])
                        self.details_pane.clear()
            else:
                messagebox.showwarning("Warning", "Please select a control to delete.")
        else:
            messagebox.showwarning("Warning", "Please select a control to delete.")

    def delete_group(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            tags = item["tags"]
            if "group" in tags:
                group_id = item["values"][0]
                group = self.find_group_by_id(group_id)
                if group:
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete group '{group_id}' and all its controls?"):
                        self.catalog.groups.remove(group)
                        self.tree.delete(selected[0])
                        self.details_pane.clear()
            else:
                messagebox.showwarning("Warning", "Please select a group to delete.")
        else:
            messagebox.showwarning("Warning", "Please select a group to delete.")

    def save_changes(self):
        try:
            self.details_pane.save_current()
            save_catalog(self.catalog, "data/NIST_SP-800-53_rev5_catalog.json")
            if isinstance(self.details_pane.current_object, ControlGroup):
                group = self.details_pane.current_object
                item = self.find_tree_item_by_id(group.id)
                if item:
                    self.tree.item(item, values=(group.id, group.title))
            elif isinstance(self.details_pane.current_object, Control):
                control = self.details_pane.current_object
                item = self.find_tree_item_by_id(control.id)
                if item:
                    self.tree.item(item, values=(control.id, control.title))
            messagebox.showinfo("Success", "Changes saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

if __name__ == "__main__":
    with open("data/NIST_SP-800-53_rev5_catalog.json", "r") as f:
        catalog_data = json.load(f)
    catalog = Catalog(**catalog_data)
    root = tk.Tk()
    app = CatalogManager(catalog, root)
    root.mainloop()
