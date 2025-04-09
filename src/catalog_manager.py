# catalog_manager.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from oscal_pydantic.catalog import Catalog, ControlGroup, Control
import os
from PIL import Image, ImageTk
try:
    import darkdetect  # Optional, for better theme detection
    DARKDETECT_AVAILABLE = True
except ImportError:
    DARKDETECT_AVAILABLE = False
from details_pane import DetailsPane
from utils import save_catalog

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
