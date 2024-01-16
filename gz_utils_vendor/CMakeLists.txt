cmake_minimum_required(VERSION 3.10)
project(gz_utils_vendor)

# Project-specific settings
set(LIB_DESIGNATOR utils)
set(LIB_VER_MAJOR 2)
set(LIB_VER_MINOR 2)
set(LIB_VER_PATCH 0)

# Derived variables
set(LIB_NAME gz-${LIB_DESIGNATOR})
set(LIB_NAME_FULL ${LIB_NAME}${LIB_VER_MAJOR})
set(LIB_VER ${LIB_VER_MAJOR}.${LIB_VER_MINOR}.${LIB_VER_PATCH})

find_package(ament_cmake_core REQUIRED)
find_package(ament_cmake_vendor_package REQUIRED)

find_package(gz_cmake_vendor REQUIRED)

find_package(${LIB_NAME_FULL} ${LIB_VER} QUIET)
ament_vendor(gz_${LIB_DESIGNATOR}_vendor
  SATISFIED ${${LIB_NAME_FULL}_FOUND}
  VCS_URL https://github.com/gazebosim/${LIB_NAME}.git
  VCS_VERSION ${LIB_NAME_FULL}_${LIB_VER}
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

ament_package(
  CONFIG_EXTRAS_POST "gz_utils_vendor-extras.cmake.in"
)
