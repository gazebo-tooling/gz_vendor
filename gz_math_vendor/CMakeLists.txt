cmake_minimum_required(VERSION 3.10)
project(gz_math_vendor)

# Project-specific settings
set(LIB_DESIGNATOR math)
set(LIB_VER_MAJOR 7)
set(LIB_VER_MINOR 3)
set(LIB_VER_PATCH 0)

# Derived variables
set(LIB_NAME gz-${LIB_DESIGNATOR})
set(LIB_NAME_FULL ${LIB_NAME}${LIB_VER_MAJOR})
set(LIB_VER ${LIB_VER_MAJOR}.${LIB_VER_MINOR}.${LIB_VER_PATCH})

find_package(ament_cmake_core REQUIRED)
find_package(ament_cmake_vendor_package REQUIRED)
find_package(ament_cmake_export_dependencies REQUIRED)

find_package(gz_cmake_vendor REQUIRED)
find_package(gz_utils_vendor REQUIRED)

# Set the VERSION_MATCH to "EXACT" by default, but relax the requirement
# if we are users are building from source (determined by the GZ_BUILD_FROM_SOURCE environment variable)
# or if explicitly told to do so by the GZ_RELAX_VERSION_MATCH environment variable.
set(VERSION_MATCH "EXACT")
if (NOT $ENV{GZ_BUILD_FROM_SOURCE} STREQUAL "")
  set(VERSION_MATCH "")
endif()

if (NOT $ENV{GZ_RELAX_VERSION_MATCH} STREQUAL "")
  set(VERSION_MATCH "")
endif()

find_package(${LIB_NAME_FULL} ${VERSION_MATCH} ${LIB_VER} COMPONENTS all QUIET)
ament_vendor(gz_${LIB_DESIGNATOR}_vendor
  SATISFIED ${${LIB_NAME_FULL}_FOUND}
  VCS_URL https://github.com/gazebosim/${LIB_NAME}.git
  VCS_VERSION ${LIB_NAME_FULL}_${LIB_VER}
  CMAKE_ARGS
    -DBUILD_DOCS:BOOL=OFF
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

ament_export_dependencies(
  gz_cmake_vendor
  gz_utils_vendor
)
ament_package(
  CONFIG_EXTRAS_POST "gz_math_vendor-extras.cmake.in"
)
message("cmake prefix: ${CMAKE_PREFIX_PATH}")
