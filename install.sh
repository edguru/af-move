#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Movement Labs AI Assistant installation...${NC}"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo -e "${GREEN}Python version $python_version is compatible${NC}"
else
    echo -e "${RED}Error: Python version must be 3.10 or higher (current: $python_version)${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install system dependencies for unstructured
echo -e "${YELLOW}Installing system dependencies...${NC}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo apt-get update
    sudo apt-get install -y libmagic1 poppler-utils tesseract-ocr libreoffice
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew install libmagic poppler tesseract libreoffice
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p data/vector_db
mkdir -p data/docs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your credentials.${NC}"
fi

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Edit the .env file with your credentials"
echo -e "2. Run the bot in test mode: TEST_MODE=true python src/main.py"
echo -e "3. Once tested, run in production: python src/main.py" 