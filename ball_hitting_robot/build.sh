#!/bin/bash
###############################################################################
# Build Script for Ball-Hitting Robot Project
#
# This script builds all ROS2 packages in the workspace
#
# Usage:
#   ./build.sh          # Build all packages
#   ./build.sh clean    # Clean and rebuild all packages
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Ball-Hitting Robot - Build Script${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Source ROS2 Humble
echo -e "${YELLOW}[1/4] Sourcing ROS2 Humble...${NC}"
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
    echo -e "${GREEN}✓ ROS2 Humble sourced${NC}"
else
    echo -e "${RED}✗ ROS2 Humble not found. Please install ROS2 Humble.${NC}"
    exit 1
fi
echo ""

# Check if clean build is requested
if [ "$1" == "clean" ]; then
    echo -e "${YELLOW}[2/4] Cleaning previous build...${NC}"
    rm -rf build install log
    echo -e "${GREEN}✓ Clean complete${NC}"
else
    echo -e "${YELLOW}[2/4] Keeping previous build${NC}"
fi
echo ""

# Check dependencies
echo -e "${YELLOW}[3/4] Checking dependencies...${NC}"

# Check for colcon
if ! command -v colcon &> /dev/null; then
    echo -e "${RED}✗ colcon not found. Installing...${NC}"
    sudo apt install -y python3-colcon-common-extensions
fi

# Check for OpenCV
if ! python3 -c "import cv2" &> /dev/null; then
    echo -e "${YELLOW}⚠ OpenCV not found. Installing...${NC}"
    pip3 install opencv-python
fi

echo -e "${GREEN}✓ Dependencies checked${NC}"
echo ""

# Build the workspace
echo -e "${YELLOW}[4/4] Building workspace...${NC}"
echo -e "${YELLOW}Running: colcon build --symlink-install${NC}"
echo ""

if colcon build --symlink-install; then
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Source the workspace:"
    echo "   ${GREEN}source install/setup.bash${NC}"
    echo ""
    echo "2. Launch the system:"
    echo "   ${GREEN}ros2 launch gazebo_simulation full_system.launch.py${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}======================================${NC}"
    echo -e "${RED}✗ Build failed!${NC}"
    echo -e "${RED}======================================${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "1. Check error messages above"
    echo "2. Verify all dependencies are installed"
    echo "3. Try clean build: ./build.sh clean"
    echo ""
    exit 1
fi
