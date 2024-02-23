# Scripts to create and update vendor packages

- `create_vendor_package.py`: Given a `package.xml` file of the upstream Gazebo
  library, it generates new `package.xml` and `CMakeLists.txt` files for the
  corresponding vendor package. This can also be used to update an existing
  vendor package when there's an update in the upstream gz library.

- `create_new_vendor_package.py`: Given a `package.xml` file, creates a vendor
  package directory with files from `create_vendor_package.py` and other files.
