cmake_minimum_required(VERSION 3.10)
project(test_gz_vendor)

find_package(ament_cmake_core REQUIRED)

find_package(gz_math_vendor REQUIRED)
find_package(gz_utils_vendor REQUIRED)

add_executable(test_gz_vendor src/main.cc)
target_link_libraries(test_gz_vendor PUBLIC gz-math gz-utils::cli)

find_package(ament_cmake_test REQUIRED)
if(BUILD_TESTING)
  find_package(ament_cmake_lint_cmake REQUIRED)
  find_package(ament_cmake_copyright REQUIRED)
  find_package(ament_cmake_xmllint REQUIRED)

  ament_lint_cmake()
  ament_copyright()
  ament_xmllint()
endif()

ament_package()
