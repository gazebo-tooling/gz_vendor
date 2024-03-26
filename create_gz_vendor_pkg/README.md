# Scripts to create and update vendor packages

- `create_vendor_package.py`: Given a `package.xml` file of the upstream Gazebo
  library, it generates new `package.xml` and `CMakeLists.txt` files as well as
  other files needed for the corresponding vendor package. This can also be used
  to update an existing vendor package when there's an update in the upstream gz
  library.
