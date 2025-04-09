# utils.py
import json
from oscal_pydantic.catalog import Catalog

def save_catalog(catalog: Catalog, file_path: str):
    """Save the catalog to a JSON file."""
    with open(file_path, 'w') as f:
        f.write(catalog.json(exclude_none=True, indent=2))
