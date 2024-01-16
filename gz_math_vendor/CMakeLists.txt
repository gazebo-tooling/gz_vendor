cmake_minimum_required(VERSION 3.10)
project(gz_math_vendor)

find_package(ament_cmake_core REQUIRED)
find_package(ament_cmake_vendor_package REQUIRED)

find_package(gz_cmake_vendor REQUIRED)
find_package(gz_utils_vendor REQUIRED)


find_package(gz-math7 7.3.0 QUIET)

ament_vendor(gz_math_vendor
  SATISFIED ${gz-math7_FOUND}
  VCS_URL https://github.com/gazebosim/gz-math.git
  VCS_VERSION gz-math7_7.3.0
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
