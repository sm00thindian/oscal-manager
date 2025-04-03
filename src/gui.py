# src/gui.py
import tkinter as tk
from tkinter import ttk
from oscal_handler import load_catalog, save_catalog

class CatalogGUI:
    def __init__(self, catalog):
        self.catalog = catalog
        self.root = tk.Tk()
        self.root.title("OSCAL Catalog Manager")
        self.root.geometry("800x900")  # Increased height for more fields
        self.root.resizable(False, False)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Title"), show="headings", height=15)
        self.tree.heading("ID", text="Control ID")
        self.tree.heading("Title", text="Title")
        self.tree.column("ID", width=150)
        self.tree.column("Title", width=600)
        self.tree.pack(fill=tk.BOTH, padx=10, pady=10)

        self.edit_frame = tk.Frame(self.root)
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

        # Related Links
        tk.Label(self.edit_frame, text="Related Links:").grid(row=4, column=0, sticky="ne")
        self.links_var = tk.StringVar()
        self.links_text = tk.Text(self.edit_frame, height=3, width=80)
        self.links_text.grid(row=4, column=1, pady=5)
        self.links_text.bind("<<Modified>>", self.update_links_var)

        # Control Enhancements
        tk.Label(self.edit_frame, text="Enhancements:").grid(row=5, column=0, sticky="ne")
        self.enhancements_var = tk.StringVar()
        self.enhancements_text = tk.Text(self.edit_frame, height=3, width=80)
        self.enhancements_text.grid(row=5, column=1, pady=5)
        self.enhancements_text.bind("<<Modified>>", self.update_enhancements_var)

        tk.Button(self.edit_frame, text="Save Changes", command=self.save_changes).grid(row=6, column=1, pady=10, sticky="e")

        self.populate_tree()
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def populate_tree(self):
        """Populate the treeview with catalog controls."""
        for group in self.catalog.groups or []:
            group_node = self.tree.insert("", "end", text=group.id, values=(group.id, group.title))
            for control in group.controls or []:
                self.tree.insert(group_node, "end", text=control.id, values=(control.id, control.title))

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
                    self.links_text.delete("1.0", tk.END)
                    self.links_text.insert("1.0", "")
                    self.links_var.set("")
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
                                    # Try different attribute names for prose
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

                        # Related Links
                        links = []
                        if hasattr(control, "links") and control.links:
                            for link in control.links:
                                text = getattr(link, "text", "None")
                                href = getattr(link, "href", "")
                                links.append(f"{text} ({href})")
                        links_text = "\n".join(links)
                        self.links_text.delete("1.0", tk.END)
                        self.links_text.insert("1.0", links_text)
                        self.links_var.set(links_text)

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

    def update_links_var(self, event):
        self.links_var.set(self.links_text.get("1.0", tk.END).strip())
        self.links_text.edit_modified(False)

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
            new_links = self.links_var.get().split("\n")
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
                        # Update Links
                        if hasattr(control, "links") and control.links:
                            for i, link_text in enumerate(new_links):
                                if i < len(control.links) and link_text:
                                    text, href = link_text.rsplit(" (", 1) if " (" in link_text else (link_text, "")
                                    href = href.rstrip(")") if href else ""
                                    control.links[i].text = text
                                    control.links[i].href = href
                        break
            self.tree.item(selected[0], values=(item_id, new_title))
            save_catalog(self.catalog, "data/NIST_SP-800-53_rev5_catalog.json")
            print("Changes saved!")

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
