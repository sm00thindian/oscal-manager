# src/main.py
from gui import CatalogGUI
from oscal_handler import load_catalog

if __name__ == "__main__":
    catalog = load_catalog("data/catalog.json")
    app = CatalogGUI(catalog)
    app.run()
