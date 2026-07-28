cmake_minimum_required(VERSION 3.8)
project(boe_robot_description)

# Package này chỉ chứa URDF, mesh, launch và config.
# Nó không biên dịch chương trình C/C++.
find_package(ament_cmake REQUIRED)

# Chép dữ liệu robot vào thư mục install của ROS 2.
install(
  DIRECTORY
    urdf
    meshes
    launch
    rviz
    config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)

  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)

  ament_lint_auto_find_test_dependencies()
endif()

ament_package()