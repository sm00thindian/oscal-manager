#!/bin/bash

# setup.sh: Automates the setup and initialization of the OSCAL Manager application

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Python 3.10
echo -e "${YELLOW}Checking for Python 3.10...${NC}"
if ! command -v python3.10 &> /dev/null; then
    echo -e "${RED}Error: Python 3.10 is not installed.${NC}"
    echo "Please install Python 3.10 following the instructions in README.md."
    exit 1
fi

# Check for Tkinter
echo -e "${YELLOW}Checking for Tkinter...${NC}"
if ! python3.10 -c "import tkinter" &> /dev/null; then
    echo -e "${RED}Error: Tkinter is not available for Python 3.10.${NC}"
    echo "Please install Tkinter following the platform-specific instructions in README.md."
    exit 1
fi

# Create and activate virtual environment
echo -e "${YELLOW}Creating virtual environment (venv310)...${NC}"
if [ -d "venv310" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3.10 -m venv venv310
fi

# Activate the virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv310/Scripts/activate
else
    source venv310/bin/activate
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Download NIST SP 800-53 catalog if not present
echo -e "${YELLOW}Checking for NIST SP 800-53 catalog...${NC}"
if [ -f "data/NIST_SP-800-53_rev5_catalog.json" ]; then
    echo "NIST SP 800-53 catalog already exists. Skipping download."
else
    echo "Downloading NIST SP 800-53 Rev 5 catalog..."
    mkdir -p data
    curl -o data/NIST_SP-800-53_rev5_catalog.json https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json
fi

# Run the application
echo -e "${YELLOW}Starting OSCAL Manager...${NC}"
python src/main.py

echo -e "${GREEN}Setup and initialization complete!${NC}"
