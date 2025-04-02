# src/gui.py
import tkinter as tk
from tkinter import ttk
from oscal_handler import load_catalog, save_catalog

class CatalogGUI:
    def __init__(self, catalog):
        self.catalog = catalog
        self.root = tk.Tk()
        self.root.title("OSCAL Catalog Manager")
        
        # Treeview for catalog hierarchy
        self.tree = ttk.Treeview(self.root, columns=("ID", "Title"), show="headings")
        self.tree.heading("ID", text="Control ID")
        self.tree.heading("Title", text="Title")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate tree with catalog data
        self.populate_tree()
        
        # Entry field for editing title
        self.title_var = tk.StringVar()
        tk.Label(self.root, text="Title:").pack()
        self.title_entry = tk.Entry(self.root, textvariable=self.title_var)
        self.title_entry.pack()
        
        # Save button
        tk.Button(self.root, text="Save Changes", command=self.save_changes).pack(pady=5)
        
        # Bind tree selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def populate_tree(self):
        """Populate the treeview with catalog controls."""
        for group in self.catalog.groups or []:
            group_node = self.tree.insert("", "end", text=group.id, values=(group.id, group.title))
            for control in group.controls or []:
                self.tree.insert(group_node, "end", text=control.id, values=(control.id, control.title))

    def on_select(self, event):
        """Update entry field when a control is selected."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.title_var.set(item["values"][1])  # Set title in entry field

    def save_changes(self):
        """Save changes to the catalog and update tree."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            control_id = item["values"][0]
            new_title = self.title_var.get()
            # Update the catalog object
            for group in self.catalog.groups or []:
                for control in group.controls or []:
                    if control.id == control_id:
                        control.title = new_title
                        break
            # Update tree display
            self.tree.item(selected[0], values=(control_id, new_title))
            # Save to file
            save_catalog(self.catalog, "data/catalog.json")
            print("Changes saved!")

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
