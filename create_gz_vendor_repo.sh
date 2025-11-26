#!/bin/bash

git init
git add *
git commit -as -m "Initial import"
gh repo create --public --source . --push gazebo-release/$(basename $PWD)

