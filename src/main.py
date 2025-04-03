from gui import CatalogManager
from oscal_handler import load_catalog
import tkinter as tk

if __name__ == "__main__":
    catalog = load_catalog("data/NIST_SP-800-53_rev5_catalog.json")
    root = tk.Tk()
    app = CatalogManager(catalog, root)
    root.mainloop()
