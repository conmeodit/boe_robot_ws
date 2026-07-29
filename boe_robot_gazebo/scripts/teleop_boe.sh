#!/usr/bin/env bash

set -e

export ROS_DOMAIN_ID=69
export ROS_LOCALHOST_ONLY=0

source /opt/ros/humble/setup.bash
source "${HOME}/boe_robot_ws/install/setup.bash"

existing_teleop_pid="$(
  pgrep -f '/opt/ros/humble/lib/teleop_twist_keyboard/teleop_twist_keyboard' \
    | head -n 1 \
    || true
)"

if [[ -n "${existing_teleop_pid}" ]]; then
  printf '%s\n' \
    "Teleop đã chạy ở PID ${existing_teleop_pid}." \
    'Không mở thêm teleop vì hai publisher sẽ ghi đè lệnh /cmd_vel.'
  exec bash
fi

clear
printf '%s\n' \
  'BOE ROBOT TELEOP' \
  'Giữ cửa sổ này được chọn và chuyển bàn phím sang ENG.' \
  'i: tiến | ,: lùi | j: quay trái | l: quay phải | k: dừng' \
  'u: tiến-trái | o: tiến-phải' \
  'm: lùi-phải | .: lùi-trái'

set +e
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -p speed:=0.05 \
  -p turn:=0.5
status=$?
set -e

printf '\nTeleop đã dừng với mã %s.\n' "${status}"
exec bash
