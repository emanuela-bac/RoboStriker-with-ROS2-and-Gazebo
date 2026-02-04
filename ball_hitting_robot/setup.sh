#!/bin/bash
###############################################################################
# Setup Script for Ball-Hitting Robot Project
#
# This script installs all required dependencies for the project
#
# Usage:
#   ./setup.sh
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Ball-Hitting Robot - Setup Script${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run this script as root${NC}"
    exit 1
fi

# Check Ubuntu version
echo -e "${YELLOW}[1/6] Checking system requirements...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS: $NAME $VERSION"
    if [[ "$VERSION_ID" != "22.04" ]]; then
        echo -e "${YELLOW}⚠ Warning: This project is designed for Ubuntu 22.04${NC}"
        echo -e "${YELLOW}  You have Ubuntu $VERSION_ID. Continue anyway? (y/n)${NC}"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠ Warning: Could not detect OS version${NC}"
fi
echo -e "${GREEN}✓ System check complete${NC}"
echo ""

# Update package list
echo -e "${YELLOW}[2/6] Updating package list...${NC}"
sudo apt update
echo -e "${GREEN}✓ Package list updated${NC}"
echo ""

# Install ROS2 Humble (if not already installed)
echo -e "${YELLOW}[3/6] Checking ROS2 Humble installation...${NC}"
if [ ! -f "/opt/ros/humble/setup.bash" ]; then
    echo -e "${YELLOW}ROS2 Humble not found. Installing...${NC}"
    echo ""
    
    # Add ROS2 repository
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y universe
    sudo apt update && sudo apt install -y curl
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
    
    # Install ROS2 Humble
    sudo apt update
    sudo apt install -y ros-humble-desktop
    
    echo -e "${GREEN}✓ ROS2 Humble installed${NC}"
else
    echo -e "${GREEN}✓ ROS2 Humble already installed${NC}"
fi
echo ""

# Install Gazebo
echo -e "${YELLOW}[4/6] Installing Gazebo and ROS-Gazebo bridge...${NC}"
sudo apt install -y \
    ros-humble-ros-gz \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-bridge \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher
echo -e "${GREEN}✓ Gazebo installed${NC}"
echo ""

# Install Python dependencies
echo -e "${YELLOW}[5/6] Installing Python dependencies...${NC}"
sudo apt install -y \
    python3-pip \
    python3-opencv \
    python3-numpy
    
pip3 install --user opencv-python numpy

# Install ROS2 Python packages
sudo apt install -y \
    python3-colcon-common-extensions \
    ros-humble-cv-bridge
    
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Install additional tools
echo -e "${YELLOW}[6/6] Installing additional tools...${NC}"
sudo apt install -y \
    ros-humble-rqt \
    ros-humble-rqt-image-view \
    ros-humble-rviz2
echo -e "${GREEN}✓ Additional tools installed${NC}"
echo ""

# Setup ROS2 environment in bashrc (optional)
echo -e "${YELLOW}Setup ROS2 environment in ~/.bashrc? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# ROS2 Humble" >> ~/.bashrc
        echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
        echo -e "${GREEN}✓ Added ROS2 to ~/.bashrc${NC}"
    else
        echo -e "${GREEN}✓ ROS2 already in ~/.bashrc${NC}"
    fi
fi
echo ""

# Complete
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Source ROS2 (or restart terminal if added to .bashrc):"
echo "   ${GREEN}source /opt/ros/humble/setup.bash${NC}"
echo ""
echo "2. Build the project:"
echo "   ${GREEN}./build.sh${NC}"
echo ""
echo "3. Run the simulation:"
echo "   ${GREEN}./run.sh${NC}"
echo ""
echo -e "${BLUE}For more information, see README.md${NC}"
echo ""
