cmake_minimum_required(VERSION 3.10)
project(gz_utils_vendor)

find_package(ament_cmake_core REQUIRED)
find_package(ament_cmake_vendor_package REQUIRED)

find_package(gz_cmake_vendor REQUIRED)
find_package(gz-utils2 2.2.0 QUIET)

ament_vendor(gz_utils_vendor
  SATISFIED ${gz-utils2_FOUND}
  VCS_URL https://github.com/gazebosim/gz-utils.git
  VCS_VERSION gz-utils2_2.2.0
  CMAKE_ARGS
    -DBUILD_DOCS:BOOL=OFF
  GLOBAL_HOOK
)

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
