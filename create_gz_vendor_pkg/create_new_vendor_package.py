import argparse
import sys
from catkin_pkg.package import parse_package_string
from create_vendor_packages import (
    pkg_has_dsv,
    pkg_has_extra_cmake,
    remove_version, 
    create_vendor_name, 
    generate_vendor_package_files,
)
import os
import shutil
from pathlib import Path


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Parse package.xml file and generate a vendor package',
    )
    parser.add_argument(
        'input_package_xml',
        type=argparse.FileType('r', encoding='utf-8'),
        help='The path to a package.xml file',
    )
    args = parser.parse_args(argv)
    try:
        package = parse_package_string(
            args.input_package_xml.read(), filename=args.input_package_xml.name)
    except Exception as e:
        print("Error parsing '%s':" % args.input_package_xml.name, file=sys.stderr)
        raise e
    finally:
        args.input_package_xml.close()

    pkg_name_no_version = remove_version(package.name)
    vendor_name = create_vendor_name(pkg_name_no_version)
    os.mkdir(vendor_name)
    generate_vendor_package_files(package, os.path.join(vendor_name))

    templates_path = Path(__file__).resolve().parent / "templates"
    # Copy other files
    for file in ["LICENSE", "CONTRIBUTING.md"]:
        shutil.copy(templates_path / file, Path(vendor_name) / file)

    if pkg_has_extra_cmake(pkg_name_no_version):
        shutil.copy(templates_path / "extras.cmake.in", Path(vendor_name) / f"{vendor_name}-extras.cmake.in")

    if pkg_has_dsv(pkg_name_no_version):
        shutil.copy(templates_path / "vendor.dsv.in", Path(vendor_name) / f"{vendor_name}.dsv.in")

if __name__ == "__main__":
    main()
