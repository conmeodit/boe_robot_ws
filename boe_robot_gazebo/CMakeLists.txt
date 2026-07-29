cmake_minimum_required(VERSION 3.8)
project(boe_robot_gazebo)

find_package(ament_cmake REQUIRED)
find_package(gazebo REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

add_library(boe_caster_visual_plugin SHARED
  src/caster_visual_plugin.cpp
)

target_include_directories(boe_caster_visual_plugin PRIVATE
  ${GAZEBO_INCLUDE_DIRS}
)

target_link_libraries(boe_caster_visual_plugin
  ${GAZEBO_LIBRARIES}
)

ament_target_dependencies(boe_caster_visual_plugin
  gazebo_ros
  geometry_msgs
  rclcpp
  sensor_msgs
)

install(
  DIRECTORY
    launch
    worlds
    config
    models
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/teleop_boe.sh
    scripts/gzclient_boe.sh
  DESTINATION lib/${PROJECT_NAME}
)

install(
  TARGETS
    boe_caster_visual_plugin
  LIBRARY DESTINATION lib
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)

  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)

  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
