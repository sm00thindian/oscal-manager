# OSCAL Manager

OSCAL Manager is a Python application for managing compliance documents in computer readable OSCAL format with a goal for facilitating automation. It features a graphical user interface (GUI) built with Tkinter, allowing users to load, view, and edit control details from an OSCAL JSON file. This tool is designed for compliance management and security control maintenance, making it easier to navigate and update control catalogs.

## Features
- Load and parse NIST SP 800-53 Revision 5 OSCAL catalogs in JSON format.
- Display control groups and controls in a hierarchical tree view with:
  - Collapsible/expandable group nodes.
  - Visual distinction using folder and file icons for groups and controls.
  - Tooltips on hover for quick details.
- Edit group and control details (e.g., title, description, properties) in a scrollable details pane.
- Save changes back to the OSCAL JSON file.
- Cross-platform compatibility (tested on macOS; should work on Windows and Linux with adjustments).

## Prerequisites
- **Python 3.10**: Required for compatibility with dependencies.
- **Tkinter**: Python’s built-in GUI library, used for the application interface.
- A compatible operating system (developed on macOS; should work on Windows and Linux).

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/oscal-manager.git
   cd oscal-manager
   ```

2. **Install Python 3.10**:
   - **macOS**:
     - Download and install Python 3.10 from the [official Python website](https://www.python.org/downloads/release/python-3100/).
     - Ensure Tkinter is available by installing the ActiveTcl framework:
       - Download ActiveTcl 8.6 from [ActiveState](https://www.activestate.com/products/activetcl/downloads/).
       - Install ActiveTcl to provide the Tcl/Tk libraries required by Tkinter.
   - **Windows**:
     - Download and install Python 3.10 from the [official Python website](https://www.python.org/downloads/release/python-3100/).
     - During installation, ensure the "tcl/tk and IDLE" option is checked to install Tkinter.
   - **Linux**:
     - Install Python 3.10 and Tkinter using your package manager:
       - **Ubuntu/Debian**:
         ```bash
         sudo apt update
         sudo apt install python3.10 python3.10-tk
         ```
       - **Fedora**:
         ```bash
         sudo dnf install python3.10 python3-tkinter
         ```
       - **Arch Linux**:
         ```bash
         sudo pacman -S python python-tk
         ```

3. **Set Up the Environment and Run the Application**:
   Use the provided `setup.sh` script to automate the setup process:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   This script will:
   - Verify Python 3.10 and Tkinter are installed.
   - Create and activate a virtual environment (`venv310`).
   - Install dependencies from `requirements.txt`.
   - Download the NIST SP 800-53 Rev 5 catalog if not present.
   - Launch the OSCAL Manager application.

   Alternatively, you can set up the environment manually:
   ```bash
   python3.10 -m venv venv310
   source venv310/bin/activate  # On Windows: venv310\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Download the NIST SP 800-53 Catalog** (if not using `setup.sh`):
   The `data/` directory should contain an OSCAL JSON file (e.g., `NIST_SP-800-53_rev5_catalog.json`). You can download it with:
   ```bash
   curl -o data/NIST_SP-800-53_rev5_catalog.json https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json
   ```

## Usage
1. **Run the Application**:
   If you used `setup.sh`, the application will start automatically. Otherwise, run:
   ```bash
   python src/main.py
   ```
   - A fixed 800x600 window will open, displaying a tree view of control groups and controls.
   - Expand groups to view controls, with folder and file icons for visual distinction.
   - Hover over items to see tooltips with brief details.
   - Click a group or control to view and edit its details in the right pane.
   - Click "Save Changes" to update the catalog file.

2. **File Location**:
   - The application reads from and writes to `data/NIST_SP-800-53_rev5_catalog.json` by default. Adjust `src/main.py` if using a different file.

## Project Structure
```
oscal-manager/
├── src/                # Source code
│   ├── main.py         # Entry point
│   ├── gui.py          # Tkinter GUI implementation
│   ├── oscal_handler.py # OSCAL parsing logic
│   └── __init__.py
├── data/               # OSCAL JSON files (e.g., NIST_SP-800-53_rev5_catalog.json)
├── docs/               # Documentation
│   └── README.md
├── icons/              # Icon files for the GUI
│   ├── folder.png
│   └── file.png
├── requirements.txt    # Python dependencies
├── setup.sh            # Automation script for setup and initialization
└── .gitignore          # Git ignore rules
```

## Dependencies
- `oscal-pydantic==2023.3.21`: For parsing OSCAL JSON.
- `pydantic==1.10.13`: Validation library (v1 for compatibility).
- `Pillow==10.0.0`: For handling icons in the GUI.
- `tkinter`: Built-in Python GUI library (requires separate installation on some systems).

See `requirements.txt` for the full list.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please test changes with Python 3.10 and the NIST SP 800-53 Rev 5 catalog.

## License
Apache 2.0

## Acknowledgments
- Built with support from NIST’s OSCAL project: [oscal-content](https://github.com/usnistgov/oscal-content).
