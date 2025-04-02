# src/oscal_handler.py
from oscal_pydantic.catalog import Catalog
import json

def load_catalog(file_path):
    """Load an OSCAL catalog from a JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)  # Load the full JSON
        catalog_data = data["catalog"]  # Extract the "catalog" object
    return Catalog.parse_obj(catalog_data)  # Parse only the "catalog" part

def save_catalog(catalog, file_path):
    """Save an OSCAL catalog to a JSON file."""
    with open(file_path, 'w') as f:
        f.write(catalog.json(indent=2))  # Use .json() for Pydantic v1
