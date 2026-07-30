cmake_minimum_required(VERSION 3.8)
project(boe_robot_navigation)

find_package(ament_cmake REQUIRED)

# Package này chỉ chứa launch, tham số SLAM/Nav2 và cấu hình RViz.
# Không có chương trình C/C++ cần biên dịch.
install(
  DIRECTORY
    launch
    config
    maps
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
