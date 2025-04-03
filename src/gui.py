import tkinter as tk
from tkinter import ttk, messagebox
from oscal_pydantic.catalog import Catalog, ControlGroup, Control  # Updated import
from pydantic import ValidationError
import json
import webbrowser  # Added for opening external URLs

def save_catalog(catalog: Catalog, file_path: str):
    with open(file_path, 'w') as f:
        json.dump(catalog.dict(exclude_none=True), f, indent=2)

class GroupDetails(ttk.Frame):
    """Handles display and editing of group details."""
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_var = tk.StringVar()
        tk.Entry(self, textvariable=self.title_var, width=80).grid(row=0, column=1, pady=5)
        tk.Label(self, text="Properties:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        self.props_text = tk.Text(self, height=5, width=80)
        self.props_text.grid(row=1, column=1, pady=5)

    def load(self, group: ControlGroup):
        """Loads group data into the widgets."""
        self.title_var.set(group.title or "")
        props = "\n".join(f"{prop.name}: {prop.value}" for prop in group.props or [])
        self.props_text.delete("1.0", tk.END)
        self.props_text.insert("1.0", props)

    def save(self, group: ControlGroup):
        """Saves widget data back to the group object."""
        group.title = self.title_var.get()

class ControlDetails(ttk.Frame):
    """Handles display and editing of control details."""
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager  # Reference to CatalogManager for resolving links
        tk.Label(self, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_var = tk.StringVar()
        tk.Entry(self, textvariable=self.title_var, width=80).grid(row=0, column=1, pady=5)
        tk.Label(self, text="Description:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        self.desc_text = tk.Text(self, height=5, width=80)
        self.desc_text.grid(row=1, column=1, pady=5)
        tk.Label(self, text="Statement Items:").grid(row=2, column=0, sticky="ne", padx=5, pady=5)
        self.items_text = tk.Text(self, height=5, width=80)
        self.items_text.grid(row=2, column=1, pady=5)
        tk.Label(self, text="Properties:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        self.props_text = tk.Text(self, height=3, width=80)
        self.props_text.grid(row=3, column=1, pady=5)
        tk.Label(self, text="Responsible Roles:").grid(row=4, column=0, sticky="ne", padx=5, pady=5)
        self.roles_text = tk.Text(self, height=2, width=80)
        self.roles_text.grid(row=4, column=1, pady=5)
        tk.Label(self, text="Implementation Status:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.status_var = tk.StringVar()
        tk.Entry(self, textvariable=self.status_var, width=80).grid(row=5, column=1, pady=5)
        tk.Label(self, text="References:").grid(row=6, column=0, sticky="ne", padx=5, pady=5)
        self.refs_text = tk.Text(self, height=3, width=80)
        self.refs_text.grid(row=6, column=1, pady=5)
        tk.Label(self, text="Related Links:").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
        self.links_frame = ttk.Frame(self)
        self.links_frame.grid(row=7, column=1, pady=5, sticky="w")
        self.link_labels = []
        tk.Label(self, text="Enhancements:").grid(row=8, column=0, sticky="ne", padx=5, pady=5)
        self.enhancements_text = tk.Text(self, height=3, width=80)
        self.enhancements_text.grid(row=8, column=1, pady=5)

    def load(self, control: Control):
        self.title_var.set(control.title or "")
        desc = ""
        for part in control.parts or []:
            if part.name == "statement" and part.prose:
                desc += part.prose + "\n"
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", desc.strip())
        items = "\n".join(part.prose for part in control.parts or [] if part.name == "item")
        self.items_text.delete("1.0", tk.END)
        self.items_text.insert("1.0", items or "No statement items.")
        props = "\n".join(f"{prop.name}: {prop.value}" for prop in control.props or [])
        self.props_text.delete("1.0", tk.END)
        self.props_text.insert("1.0", props or "No properties.")
        roles = "\n".join(link.role_id for link in control.links or [] if link.rel == "responsible-role")
        self.roles_text.delete("1.0", tk.END)
        self.roles_text.insert("1.0", roles or "No responsible roles.")
        status = next((prop.value for prop in control.props or [] if prop.name == "implementation-status"), "")
        self.status_var.set(status)
        refs = "\n".join(link.href for link in control.links or [] if link.rel == "reference")
        self.refs_text.delete("1.0", tk.END)
        self.refs_text.insert("1.0", refs or "No references.")
        
        # Enhanced handling of related links
        for label in self.link_labels:
            label.destroy()
        self.link_labels = []
        for link in control.links or []:
            if link.rel == "related":
                href = link.href
                if href.startswith("#"):  # Internal reference
                    target_id = href[1:]
                    control_title = self.manager.get_control_title_by_id(target_id)
                    if control_title:
                        display_text = f"{control_title} ({target_id})"
                        lbl = tk.Label(self.links_frame, text=display_text, fg="blue", cursor="hand2")
                        lbl.pack(anchor="w")
                        lbl.bind("<Button-1>", lambda e, tid=target_id: self.manager.select_control_by_id(tid))
                    else:
                        resource_title = self.manager.get_resource_title_by_uuid(target_id)
                        if resource_title:
                            display_text = f"{resource_title} ({target_id})"
                            lbl = tk.Label(self.links_frame, text=display_text)
                            lbl.pack(anchor="w")
                        else:
                            display_text = f"Unknown Reference ({href})"
                            lbl = tk.Label(self.links_frame, text=display_text)
                            lbl.pack(anchor="w")
                else:  # External URL
                    display_text = href
                    lbl = tk.Label(self.links_frame, text=display_text, fg="blue", cursor="hand2")
                    lbl.pack(anchor="w")
                    lbl.bind("<Button-1>", lambda e, url=href: webbrowser.open(url))
                self.link_labels.append(lbl)
        
        enhancements = "\n".join(f"{ctrl.id}: {ctrl.title}" for ctrl in control.controls or [])
        self.enhancements_text.delete("1.0", tk.END)
        self.enhancements_text.insert("1.0", enhancements or "No enhancements.")

    def save(self, control: Control):
        control.title = self.title_var.get()
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
    """Manages switching between group and control details."""
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager  # Reference to CatalogManager
        self.group_details = GroupDetails(self)
        self.control_details = ControlDetails(self, manager)  # Pass manager to ControlDetails
        self.no_selection_label = tk.Label(self, text="Select a group or control to edit")
        self.no_selection_label.grid(row=0, column=0, padx=5, pady=5)
        self.current_details = None
        self.current_object = None

    def show_group(self, group: ControlGroup):
        """Displays group details."""
        self.control_details.grid_remove()
        self.group_details.grid(row=0, column=0, padx=5, pady=5)
        self.group_details.load(group)
        self.current_details = self.group_details
        self.current_object = group
        self.no_selection_label.grid_remove()

    def show_control(self, control: Control):
        """Displays control details."""
        self.group_details.grid_remove()
        self.control_details.grid(row=0, column=0, padx=5, pady=5)
        self.control_details.load(control)
        self.current_details = self.control_details
        self.current_object = control
        self.no_selection_label.grid_remove()

    def clear(self):
        """Clears the details pane."""
        self.group_details.grid_remove()
        self.control_details.grid_remove()
        self.no_selection_label.grid(row=0, column=0)
        self.current_details = None
        self.current_object = None

    def save_current(self):
        """Saves the current details to the object."""
        if self.current_details and self.current_object:
            self.current_details.save(self.current_object)

class CatalogManager:
    """Main GUI class that manages the catalog interface."""
    def __init__(self, catalog: Catalog, root: tk.Tk):
        self.catalog = catalog
        self.root = root
        self.root.title("OSCAL Catalog Manager")
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(main_frame, columns=("ID", "Title"), show="headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.column("ID", width=150)
        self.tree.column("Title", width=600)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.details_pane = DetailsPane(main_frame, self)  # Pass self as manager
        self.details_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Button(self.root, text="Save Changes", command=self.save_changes).pack(pady=10)
        for group in self.catalog.groups or []:
            group_node = self.tree.insert("", "end", text=group.id, values=(group.id, group.title), tags=("group",))
            for control in group.controls or []:
                self.tree.insert(group_node, "end", text=control.id, values=(control.id, control.title), tags=("control",))
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.details_pane.clear()

    def on_tree_select(self, event):
        """Handles tree selection events."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            tags = item["tags"]
            item_id = item["values"][0]
            if "group" in tags:
                group = self.find_group_by_id(item_id)
                if group:
                    self.details_pane.show_group(group)
            elif "control" in tags:
                control = self.find_control_by_id(item_id)
                if control:
                    self.details_pane.show_control(control)
        else:
            self.details_pane.clear()

    def find_group_by_id(self, group_id: str) -> ControlGroup:
        """Finds a group by ID."""
        for group in self.catalog.groups or []:
            if group.id == group_id:
                return group
        return None

    def find_control_by_id(self, control_id: str) -> Control:
        """Finds a control by ID."""
        for group in self.catalog.groups or []:
            for control in group.controls or []:
                if control.id == control_id:
                    return control
        return None

    def find_tree_item_by_id(self, target_id):
        """Find a tree item by its control ID."""
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == target_id:
                return item
            for child in self.tree.get_children(item):
                if self.tree.item(child, "values")[0] == target_id:
                    return child
        return None

    def get_control_title_by_id(self, control_id):
        """Get the title of a control by its ID."""
        control = self.find_control_by_id(control_id)
        return control.title if control else None

    def get_resource_title_by_uuid(self, uuid):
        """Get the title of a resource by its UUID from back-matter."""
        if hasattr(self.catalog, 'back_matter') and self.catalog.back_matter:
            for resource in self.catalog.back_matter.resources or []:
                if resource.uuid == uuid:
                    return resource.title
        return None

    def select_control_by_id(self, control_id):
        """Select a control in the tree by its ID."""
        item = self.find_tree_item_by_id(control_id)
        if item:
            self.tree.selection_set(item)
            self.tree.see(item)
        else:
            messagebox.showinfo("Not Found", f"Control {control_id} not found in the catalog.")

    def save_changes(self):
        """Saves changes to the catalog file."""
        try:
            self.details_pane.save_current()
            save_catalog(self.catalog, "data/NIST_SP-800-53_rev5_catalog.json")
            print("Changes saved successfully!")
        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Failed to save changes:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

if __name__ == "__main__":
    with open("data/NIST_SP-800-53_rev5_catalog.json", "r") as f:
        catalog_data = json.load(f)
    catalog = Catalog(**catalog_data)
    root = tk.Tk()
    app = CatalogManager(catalog, root)
    root.mainloop()
