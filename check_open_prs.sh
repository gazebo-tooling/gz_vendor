#!/usr/bin/env bash

# set -x
scriptDir=$(dirname "$0")
for d in gz_ogre_next_vendor gz_dartsim_vendor gz_libs/*_vendor; do 
  (cd "$scriptDir/$d" || exit; gh pr list --json url -q '.[].url' | cat );
done
