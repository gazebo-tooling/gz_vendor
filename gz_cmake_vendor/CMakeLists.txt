cmake_minimum_required(VERSION 3.10)
project(gz_cmake_vendor)

find_package(ament_cmake_core REQUIRED)
find_package(ament_cmake_vendor_package REQUIRED)

find_package(gz-cmake3 3.4.1 QUIET)

ament_vendor(gz_cmake_vendor
  SATISFIED ${gz-cmake3_FOUND}
  VCS_URL https://github.com/gazebosim/gz-cmake.git
  VCS_VERSION gz-cmake3_3.4.1
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
