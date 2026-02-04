#!/bin/bash
###############################################################################
# Run Script for Ball-Hitting Robot Project
#
# This script sources the workspace and launches the complete system
#
# Usage:
#   ./run.sh           # Launch complete system
#   ./run.sh sim       # Launch only simulation
#   ./run.sh detect    # Launch only ball detector
#   ./run.sh control   # Launch only controller
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if workspace is built
if [ ! -d "install" ]; then
    echo -e "${RED}✗ Workspace not built!${NC}"
    echo -e "${YELLOW}Please run: ./build.sh${NC}"
    exit 1
fi

# Source ROS2 and workspace
echo -e "${YELLOW}Sourcing workspace...${NC}"
source /opt/ros/humble/setup.bash
source install/setup.bash
echo -e "${GREEN}✓ Workspace sourced${NC}"
echo ""

# Parse command line argument
MODE=${1:-full}

case $MODE in
    full)
        echo -e "${GREEN}======================================${NC}"
        echo -e "${GREEN}Launching Complete Ball-Hitting System${NC}"
        echo -e "${GREEN}======================================${NC}"
        echo ""
        echo -e "${BLUE}Starting:${NC}"
        echo "  • Gazebo simulation (robot + world)"
        echo "  • Ball detection node"
        echo "  • Ball controller node"
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        ros2 launch gazebo_simulation full_system.launch.py
        ;;
    
    sim)
        echo -e "${GREEN}======================================${NC}"
        echo -e "${GREEN}Launching Gazebo Simulation Only${NC}"
        echo -e "${GREEN}======================================${NC}"
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        ros2 launch gazebo_simulation sim_robot.launch.py
        ;;
    
    detect)
        echo -e "${GREEN}======================================${NC}"
        echo -e "${GREEN}Launching Ball Detector Only${NC}"
        echo -e "${GREEN}======================================${NC}"
        echo ""
        echo -e "${YELLOW}Make sure simulation is running!${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        ros2 run perception ball_detector
        ;;
    
    control)
        echo -e "${GREEN}======================================${NC}"
        echo -e "${GREEN}Launching Ball Controller Only${NC}"
        echo -e "${GREEN}======================================${NC}"
        echo ""
        echo -e "${YELLOW}Make sure simulation and detector are running!${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        ros2 run control ball_controller
        ;;
    
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        echo ""
        echo -e "${YELLOW}Usage:${NC}"
        echo "  ./run.sh           # Launch complete system (default)"
        echo "  ./run.sh sim       # Launch only simulation"
        echo "  ./run.sh detect    # Launch only ball detector"
        echo "  ./run.sh control   # Launch only controller"
        exit 1
        ;;
esac
