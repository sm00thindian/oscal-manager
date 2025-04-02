# src/oscal_handler.py
from oscal_pydantic.catalog import Catalog

def load_catalog(file_path):
    """Load an OSCAL catalog from a JSON file."""
    return Catalog.parse_file(file_path)

def save_catalog(catalog, file_path):
    """Save an OSCAL catalog to a JSON file."""
    with open(file_path, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
