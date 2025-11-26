#!/bin/bash

distro=$1

if [[ -z $distro ]]; then
  echo "Distro argument needed"
  exit 1
fi

branch=$(git rev-parse --abbrev-ref HEAD --symbolic)
package=$(basename $PWD)

echo "Distro: $distro"
echo "Branch: $branch"
echo "Package: $package"

read -p "Continue[Yn]? " -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]
then
  bosc-launch ros2ci ci_launcher  CI_ROS_DISTRO=$distro CI_BRANCH_TO_TEST=$branch CI_ROS2_REPOS_URL=https://raw.githubusercontent.com/ros2/ros2/$distro/ros2.repos "CI_BUILD_ARGS=--event-handlers console_cohesion+ console_package_list+ --cmake-args -DINSTALL_EXAMPLES=OFF -DSECURITY=ON -DAPPEND_PROJECT_NAME_TO_INCLUDEDIR=ON  --packages-above-and-dependencies $package" CI_TEST_ARGS="--event-handlers console_cohesion+ --retest-until-pass 2 --ctest-args -LE xfail --pytest-args -m 'not xfail' --executor sequential --packages-above $package"
fi
