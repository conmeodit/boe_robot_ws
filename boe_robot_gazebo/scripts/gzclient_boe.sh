#!/usr/bin/env bash

set -e

source /opt/ros/humble/setup.bash
source "${HOME}/boe_robot_ws/install/setup.bash"

export GAZEBO_MODEL_PATH="/usr/share/gazebo-11/models:${HOME}/boe_robot_ws/install/boe_robot_description/share"
export GAZEBO_MODEL_DATABASE_URI=""

exec gzclient --gui-client-plugin=libgazebo_ros_eol_gui.so
