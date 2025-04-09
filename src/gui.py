# gui.py
import tkinter as tk
import json
from oscal_pydantic.catalog import Catalog
from catalog_manager import CatalogManager

if __name__ == "__main__":
    with open("data/NIST_SP-800-53_rev5_catalog.json", "r") as f:
        catalog_data = json.load(f)
    catalog = Catalog(**catalog_data)
    root = tk.Tk()
    app = CatalogManager(catalog, root)
    root.mainloop()
