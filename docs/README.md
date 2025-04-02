# OSCAL Manager

A Python application for managing NIST SP 800-53 control catalogs in OSCAL format, featuring a graphical user interface (GUI) built with Tkinter. This tool allows users to load, view, and edit control details from an OSCAL JSON file, making it useful for compliance management and security control maintenance.

## Features
- Load and parse NIST SP 800-53 Revision 5 OSCAL catalogs.
- Display controls in a hierarchical tree view.
- Edit control details (e.g., title, description) with a fixed-size GUI.
- Save changes back to the OSCAL JSON file.

## Prerequisites
- Python 3.10 (recommended due to compatibility with dependencies).
- macOS (developed and tested on macOS; may work on other platforms with adjustments).
- Homebrew (for macOS dependency management).

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/oscal-manager.git
   cd oscal-manager
   ```

2. **Set Up Python 3.10** (macOS with Homebrew):
   ```bash
   brew install python@3.10
   brew install python-tk@3.10  # For Tkinter support
   ```

3. **Create and Activate a Virtual Environment**:
   ```bash
   /opt/homebrew/bin/python3.10 -m venv venv310
   source venv310/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Download the NIST SP 800-53 Catalog** (optional):
   The `data/` directory should contain an OSCAL JSON file (e.g., `NIST_SP-800-53_rev5_catalog.json`). You can download it with:
   ```bash
   curl -o data/NIST_SP-800-53_rev5_catalog.json https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json
   ```

## Usage
1. **Run the Application**:
   ```bash
   python src/main.py
   ```
   - A fixed 800x600 window will open, showing a tree view of control groups and controls.
   - Click a control to edit its title and description.
   - Click "Save Changes" to update the catalog file.

2. **File Location**:
   - The application reads from and writes to `data/NIST_SP-800-53_rev5_catalog.json` by default. Adjust `src/main.py` if using a different file.

## Project Structure
```
oscal-manager/
├── src/                # Source code
│   ├── main.py         # Entry point
│   ├── gui.py          # Tkinter GUI implementation
│   └── oscal_handler.py # OSCAL parsing logic
├── data/               # OSCAL JSON files (e.g., NIST_SP-800-53_rev5_catalog.json)
├── docs/               # Documentation (e.g., README.md)
├── requirements.txt    # Python dependencies
└── .gitignore          # Git ignore rules
```

## Dependencies
- `oscal-pydantic==2023.3.21`: For parsing OSCAL JSON.
- `pydantic==1.10.13`: Validation library (v1 for compatibility).
- `tkinter`: Built-in Python GUI library (requires `python-tk@3.10` on macOS).

See `requirements.txt` for the full list.

## Contributing
Feel free to fork this repository, submit issues, or send pull requests. Ensure changes are tested with Python 3.10 and the NIST SP 800-53 Rev 5 catalog.

## License
Apache 2.0

## Acknowledgments
- Built with support from NIST’s OSCAL project: [oscal-content](https://github.com/usnistgov/oscal-content).
