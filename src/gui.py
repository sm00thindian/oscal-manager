# src/gui.py
import tkinter as tk
from tkinter import ttk
from oscal_handler import load_catalog, save_catalog

class CatalogGUI:
    def __init__(self, catalog):
        self.catalog = catalog
        self.root = tk.Tk()
        self.root.title("OSCAL Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Create a canvas and scrollbar for the entire window
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Treeview
        self.tree = ttk.Treeview(self.scrollable_frame, columns=("ID", "Title"), show="headings", height=15)
        self.tree.heading("ID", text="Control ID")
        self.tree.heading("Title", text="Title")
        self.tree.column("ID", width=150)
        self.tree.column("Title", width=600)
        self.tree.pack(fill=tk.BOTH, padx=10, pady=10)

        # Edit Frame
        self.edit_frame = ttk.Frame(self.scrollable_frame)
        self.edit_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        # Title
        tk.Label(self.edit_frame, text="Title:").grid(row=0, column=0, sticky="e")
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(self.edit_frame, textvariable=self.title_var, width=80)
        self.title_entry.grid(row=0, column=1, pady=5)

        # Description (Statement)
        tk.Label(self.edit_frame, text="Description:").grid(row=1, column=0, sticky="ne")
        self.desc_var = tk.StringVar()
        self.desc_text = tk.Text(self.edit_frame, height=5, width=80)
        self.desc_text.grid(row=1, column=1, pady=5)
        self.desc_text.bind("<<Modified>>", self.update_desc_var)

        # Statement Items
        tk.Label(self.edit_frame, text="Statement Items:").grid(row=2, column=0, sticky="ne")
        self.items_var = tk.StringVar()
        self.items_text = tk.Text(self.edit_frame, height=5, width=80)
        self.items_text.grid(row=2, column=1, pady=5)
        self.items_text.bind("<<Modified>>", self.update_items_var)

        # Properties
        tk.Label(self.edit_frame, text="Properties:").grid(row=3, column=0, sticky="ne")
        self.props_var = tk.StringVar()
        self.props_text = tk.Text(self.edit_frame, height=3, width=80)
        self.props_text.grid(row=3, column=1, pady=5)
        self.props_text.bind("<<Modified>>", self.update_props_var)

        # Responsible Roles
        tk.Label(self.edit_frame, text="Responsible Roles:").grid(row=4, column=0, sticky="ne")
        self.roles_var = tk.StringVar()
        self.roles_text = tk.Text(self.edit_frame, height=2, width=80)
        self.roles_text.grid(row=4, column=1, pady=5)
        self.roles_text.bind("<<Modified>>", self.update_roles_var)

        # Implementation Status
        tk.Label(self.edit_frame, text="Implementation Status:").grid(row=5, column=0, sticky="e")
        self.status_var = tk.StringVar()
        self.status_entry = tk.Entry(self.edit_frame, textvariable=self.status_var, width=80)
        self.status_entry.grid(row=5, column=1, pady=5)

        # References
        tk.Label(self.edit_frame, text="References:").grid(row=6, column=0, sticky="ne")
        self.refs_var = tk.StringVar()
        self.refs_text = tk.Text(self.edit_frame, height=3, width=80)
        self.refs_text.grid(row=6, column=1, pady=5)
        self.refs_text.bind("<<Modified>>", self.update_refs_var)

        # Related Links (with clickable labels)
        tk.Label(self.edit_frame, text="Related Links:").grid(row=7, column=0, sticky="ne")
        self.links_frame = ttk.Frame(self.edit_frame)
        self.links_frame.grid(row=7, column=1, pady=5, sticky="w")
        self.link_labels = []  # To store clickable labels

        # Control Enhancements
        tk.Label(self.edit_frame, text="Enhancements:").grid(row=8, column=0, sticky="ne")
        self.enhancements_var = tk.StringVar()
        self.enhancements_text = tk.Text(self.edit_frame, height=3, width=80)
        self.enhancements_text.grid(row=8, column=1, pady=5)
        self.enhancements_text.bind("<<Modified>>", self.update_enhancements_var)

        tk.Button(self.edit_frame, text="Save Changes", command=self.save_changes).grid(row=9, column=1, pady=10, sticky="e")

        self.populate_tree()
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def populate_tree(self):
        """Populate the treeview with catalog controls."""
        for group in self.catalog.groups or []:
            group_node = self.tree.insert("", "end", text=group.id, values=(group.id, group.title))
            for control in group.controls or []:
                self.tree.insert(group_node, "end", text=control.id, values=(control.id, control.title))

    def find_control_by_id(self, control_id):
        """Find a control by its ID in the catalog."""
        for group in self.catalog.groups or []:
            if group.id == control_id:
                return group
            for control in group.controls or []:
                if control.id == control_id:
                    return control
        return None

    def find_resource_by_uuid(self, uuid):
        """Find a resource by its UUID in the back-matter."""
        if hasattr(self.catalog, "back_matter") and self.catalog.back_matter:
            if hasattr(self.catalog.back_matter, "resources"):
                for resource in self.catalog.back_matter.resources or []:
                    if getattr(resource, "uuid", "") == uuid:
                        return resource
        return None

    def on_link_click(self, target_id):
        """Handle clicking a related link by selecting the target in the tree."""
        # Find the tree item with the target ID
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == target_id:
                self.tree.selection_set(item)
                self.tree.see(item)
                return
            for child in self.tree.get_children(item):
                if self.tree.item(child, "values")[0] == target_id:
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    return

    def on_select(self, event):
        """Update entry fields when a group or control is selected."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            item_id = item["values"][0]
            for group in self.catalog.groups or []:
                if group.id == item_id:
                    self.title_var.set(group.title)
                    self.desc_text.delete("1.0", tk.END)
                    self.desc_text.insert("1.0", "")
                    self.desc_var.set("")
                    self.items_text.delete("1.0", tk.END)
                    self.items_text.insert("1.0", "")
                    self.items_var.set("")
                    self.props_text.delete("1.0", tk.END)
                    self.props_text.insert("1.0", "")
                    self.props_var.set("")
                    self.roles_text.delete("1.0", tk.END)
                    self.roles_text.insert("1.0", "")
                    self.roles_var.set("")
                    self.status_var.set("")
                    self.refs_text.delete("1.0", tk.END)
                    self.refs_text.insert("1.0", "")
                    self.refs_var.set("")
                    # Clear existing link labels
                    for label in self.link_labels:
                        label.destroy()
                    self.link_labels.clear()
                    self.enhancements_text.delete("1.0", tk.END)
                    self.enhancements_text.insert("1.0", "")
                    self.enhancements_var.set("")
                    return
                for control in group.controls or []:
                    if control.id == item_id:
                        self.title_var.set(control.title)

                        # Description (Statement)
                        desc = ""
                        if hasattr(control, "parts") and control.parts:
                            for part in control.parts:
                                if getattr(part, "name", "") == "statement":
                                    prose = getattr(part, "prose", getattr(part, "value", getattr(part, "text", "")))
                                    if isinstance(prose, str):
                                        desc = prose
                                    elif prose:
                                        desc = str(prose)
                                    break
                        self.desc_text.delete("1.0", tk.END)
                        self.desc_text.insert("1.0", desc)
                        self.desc_var.set(desc)

                        # Statement Items
                        items = []
                        if hasattr(control, "parts") and control.parts:
                            for part in control.parts:
                                if getattr(part, "name", "") == "item":
                                    label = ""
                                    if hasattr(part, "props") and part.props:
                                        for prop in part.props:
                                            if getattr(prop, "name", "") == "label":
                                                label = getattr(prop, "value", "")
                                                break
                                    prose = getattr(part, "prose", getattr(part, "value", getattr(part, "text", "")))
                                    if isinstance(prose, str):
                                        items.append(f"{label}: {prose}")
                                    elif prose:
                                        items.append(f"{label}: {str(prose)}")
                        items_text = "\n".join(items)
                        self.items_text.delete("1.0", tk.END)
                        self.items_text.insert("1.0", items_text)
                        self.items_var.set(items_text)

                        # Properties
                        props = []
                        if hasattr(control, "props") and control.props:
                            for prop in control.props:
                                name = getattr(prop, "name", "")
                                value = getattr(prop, "value", "")
                                props.append(f"{name}: {value}")
                        props_text = "\n".join(props)
                        self.props_text.delete("1.0", tk.END)
                        self.props_text.insert("1.0", props_text)
                        self.props_var.set(props_text)

                        # Responsible Roles
                        roles = []
                        if hasattr(control, "props") and control.props:
                            for prop in control.props:
                                if getattr(prop, "name", "") == "responsible-role":
                                    value = getattr(prop, "value", "")
                                    roles.append(value)
                        roles_text = "\n".join(roles)
                        self.roles_text.delete("1.0", tk.END)
                        self.roles_text.insert("1.0", roles_text)
                        self.roles_var.set(roles_text)

                        # Implementation Status
                        status = ""
                        if hasattr(control, "props") and control.props:
                            for prop in control.props:
                                if getattr(prop, "name", "") == "status":
                                    status = getattr(prop, "value", "")
                                    break
                        self.status_var.set(status)

                        # References
                        refs = []
                        if hasattr(control, "parts") and control.parts:
                            for part in control.parts:
                                if getattr(part, "name", "") == "reference":
                                    prose = getattr(part, "prose", getattr(part, "value", getattr(part, "text", "")))
                                    if isinstance(prose, str):
                                        refs.append(prose)
                                    elif prose:
                                        refs.append(str(prose))
                        refs_text = "\n".join(refs)
                        self.refs_text.delete("1.0", tk.END)
                        self.refs_text.insert("1.0", refs_text)
                        self.refs_var.set(refs_text)

                        # Related Links (with resolved references)
                        # Clear existing link labels
                        for label in self.link_labels:
                            label.destroy()
                        self.link_labels.clear()

                        if hasattr(control, "links") and control.links:
                            for i, link in enumerate(control.links):
                                text = getattr(link, "text", "None")
                                href = getattr(link, "href", "")
                                if href.startswith("#"):
                                    target_id = href[1:]  # Remove the "#"
                                    # Try to find a control with this ID
                                    target_control = self.find_control_by_id(target_id)
                                    if target_control:
                                        target_title = getattr(target_control, "title", target_id)
                                        display_text = f"{target_title} ({target_id})"
                                        # Create a clickable label
                                        link_label = ttk.Label(
                                            self.links_frame,
                                            text=display_text,
                                            foreground="blue",
                                            cursor="hand2"
                                        )
                                        link_label.grid(row=i, column=0, sticky="w")
                                        link_label.bind("<Button-1>", lambda e, tid=target_id: self.on_link_click(tid))
                                        self.link_labels.append(link_label)
                                    else:
                                        # Try to find a resource in back-matter
                                        target_resource = self.find_resource_by_uuid(target_id)
                                        if target_resource:
                                            target_title = getattr(target_resource, "title", target_id)
                                            display_text = f"{target_title} ({target_id})"
                                            # Display as non-clickable (resources aren't in the tree)
                                            link_label = ttk.Label(self.links_frame, text=display_text)
                                            link_label.grid(row=i, column=0, sticky="w")
                                            self.link_labels.append(link_label)
                                        else:
                                            # Fallback to original display
                                            link_label = ttk.Label(self.links_frame, text=f"{text} ({href})")
                                            link_label.grid(row=i, column=0, sticky="w")
                                            self.link_labels.append(link_label)
                                else:
                                    # External link (not clickable for now)
                                    link_label = ttk.Label(self.links_frame, text=f"{text} ({href})")
                                    link_label.grid(row=i, column=0, sticky="w")
                                    self.link_labels.append(link_label)

                        # Control Enhancements
                        enhancements = []
                        if hasattr(control, "controls") and control.controls:
                            for sub_control in control.controls:
                                sub_id = getattr(sub_control, "id", "")
                                sub_title = getattr(sub_control, "title", "")
                                enhancements.append(f"{sub_id}: {sub_title}")
                        enhancements_text = "\n".join(enhancements)
                        self.enhancements_text.delete("1.0", tk.END)
                        self.enhancements_text.insert("1.0", enhancements_text)
                        self.enhancements_var.set(enhancements_text)
                        return

    def update_desc_var(self, event):
        self.desc_var.set(self.desc_text.get("1.0", tk.END).strip())
        self.desc_text.edit_modified(False)

    def update_items_var(self, event):
        self.items_var.set(self.items_text.get("1.0", tk.END).strip())
        self.items_text.edit_modified(False)

    def update_props_var(self, event):
        self.props_var.set(self.props_text.get("1.0", tk.END).strip())
        self.props_text.edit_modified(False)

    def update_roles_var(self, event):
        self.roles_var.set(self.roles_text.get("1.0", tk.END).strip())
        self.roles_text.edit_modified(False)

    def update_refs_var(self, event):
        self.refs_var.set(self.refs_text.get("1.0", tk.END).strip())
        self.refs_text.edit_modified(False)

    def update_links_var(self, event):
        pass  # Not used since we're using labels now

    def update_enhancements_var(self, event):
        self.enhancements_var.set(self.enhancements_text.get("1.0", tk.END).strip())
        self.enhancements_text.edit_modified(False)

    def save_changes(self):
        """Save changes to the catalog and update tree."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            item_id = item["values"][0]
            new_title = self.title_var.get()
            new_desc = self.desc_var.get()
            new_items = self.items_var.get().split("\n")
            new_props = self.props_var.get().split("\n")
            new_roles = self.roles_var.get().split("\n")
            new_status = self.status_var.get()
            new_refs = self.refs_var.get().split("\n")
            # Links are not editable in this version
            for group in self.catalog.groups or []:
                if group.id == item_id:
                    group.title = new_title
                    break
                for control in group.controls or []:
                    if control.id == item_id:
                        control.title = new_title
                        # Update Description
                        if hasattr(control, "parts") and control.parts:
                            for part in control.parts:
                                if getattr(part, "name", "") == "statement":
                                    if hasattr(part, "prose"):
                                        part.prose = new_desc
                                    elif hasattr(part, "value"):
                                        part.value = new_desc
                                    elif hasattr(part, "text"):
                                        part.text = new_desc
                                    break
                        # Update Statement Items
                        if hasattr(control, "parts") and control.parts:
                            item_parts = [part for part in control.parts if getattr(part, "name", "") == "item"]
                            for i, item_text in enumerate(new_items):
                                if i < len(item_parts) and item_text:
                                    label, prose = item_text.split(": ", 1) if ": " in item_text else ("", item_text)
                                    if hasattr(item_parts[i], "prose"):
                                        item_parts[i].prose = prose
                                    elif hasattr(item_parts[i], "value"):
                                        item_parts[i].value = prose
                                    elif hasattr(item_parts[i], "text"):
                                        item_parts[i].text = prose
                        # Update Properties
                        if hasattr(control, "props") and control.props:
                            for i, prop_text in enumerate(new_props):
                                if i < len(control.props) and prop_text:
                                    name, value = prop_text.split(": ", 1) if ": " in prop_text else (control.props[i].name, prop_text)
                                    control.props[i].name = name
                                    control.props[i].value = value
                        # Update Responsible Roles
                        if hasattr(control, "props") and control.props:
                            role_props = [prop for prop in control.props if getattr(prop, "name", "") == "responsible-role"]
                            for i, role in enumerate(new_roles):
                                if i < len(role_props) and role:
                                    role_props[i].value = role
                        # Update Implementation Status
                        if hasattr(control, "props") and control.props:
                            status_prop = None
                            for prop in control.props:
                                if getattr(prop, "name", "") == "status":
                                    status_prop = prop
                                    break
                            if status_prop:
                                status_prop.value = new_status
                            else:
                                # Add new status prop if it doesn't exist
                                control.props.append(type(control.props[0])(name="status", value=new_status))
                        # Update References
                        if hasattr(control, "parts") and control.parts:
                            ref_parts = [part for part in control.parts if getattr(part, "name", "") == "reference"]
                            for i, ref_text in enumerate(new_refs):
                                if i < len(ref_parts) and ref_text:
                                    if hasattr(ref_parts[i], "prose"):
                                        ref_parts[i].prose = ref_text
                                    elif hasattr(ref_parts[i], "value"):
                                        ref_parts[i].value = ref_text
                                    elif hasattr(ref_parts[i], "text"):
                                        ref_parts[i].text = ref_text
                        break
            self.tree.item(selected[0], values=(item_id, new_title))
            save_catalog(self.catalog, "data/NIST_SP-800-53_rev5_catalog.json")
            print("Changes saved!")

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
