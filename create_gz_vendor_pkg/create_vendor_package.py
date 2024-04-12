import argparse
import sys
from catkin_pkg.package import Dependency, InvalidPackage, parse_package, parse_package_string, Package
import re
import copy
import jinja2
from pathlib import Path
import os
import shutil


GZ_LIBRARIES = [
    'gz-cmake',
    'gz-common',
    'gz-fuel-tools',
    'gz-gui',
    'gz-launch',
    'gz-math',
    'gz-msgs',
    'gz-physics',
    'gz-plugin',
    'gz-rendering',
    'gz-sensors',
    'gz-sim',
    'gz-tools',
    'gz-transport',
    'gz-utils',
    'sdformat',
]

EXTRA_VENDORED_PKGS = {
    'dartsim': 'gz_dartsim_vendor',
    'libogre-next-2.3-dev': 'gz_ogre_next_vendor',
    'libogre-next-2.3': 'gz_ogre_next_vendor',
}

# These dependencies will be removed from the package.xml provided by the upstream Gazebo library
DEPENDENCY_DISALLOW_LIST = [
    # python3-distutiol is not needed for CMake > 3.12. Also, it is currently failing to install on Noble
    'python3-distutils',
]

# These were taken from catkin_pkg's package.py file
DEPENDENCY_TYPES = [
    'build_depends',
    'buildtool_depends',
    'build_export_depends',
    'buildtool_export_depends',
    'exec_depends',
    'test_depends',
    'doc_depends',
]

def filter_dependencies(package: Package):

    def filter_impl(deps):
        return [dep for dep in deps if dep.name not in DEPENDENCY_DISALLOW_LIST]

    for dep_type in DEPENDENCY_TYPES:
        setattr(package, dep_type, filter_impl(getattr(package, dep_type)))

    return package

def remove_version(pkg_name: str):
    pkg_name_no_version = re.match('[-_a-z]*', pkg_name)
    if not pkg_name_no_version:
        raise RuntimeError("Could not parse package name")
    return pkg_name_no_version.group(0)

def create_vendor_name(pkg_name: str):
    return f"{pkg_name.replace('-', '_')}_vendor"

def is_gz_library(dep: Dependency):
    # For the purposes of this tool, ogre-next and dartsim are considered gz libraries,
    # thus, we'll use vendored versions of those packages.
    if dep.name in EXTRA_VENDORED_PKGS.keys():
        return True
    pkg_name_no_version = remove_version(dep.name)
    return pkg_name_no_version in GZ_LIBRARIES

def vendorize_gz_dependency(dep: Dependency):
    if dep.name in EXTRA_VENDORED_PKGS:
        dep.name = EXTRA_VENDORED_PKGS[dep.name]
        return
    pkg_name_no_version = remove_version(dep.name)
    dep.name = create_vendor_name(pkg_name_no_version) 

def separate_gz_deps(deps):
    gz_deps = []
    non_gz_deps = []
    for dep in deps:
        if is_gz_library(dep):
            gz_deps.append(dep)
        else:
            non_gz_deps.append(dep)
    return gz_deps, non_gz_deps

def split_version(version: str):
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if match is None:
        raise ValueError(f'Invalid version string, must be int.int.int: "{version}"')
    new_version = match.groups()
    new_version = [int(x) for x in new_version]
    return {'major': new_version[0], 'minor': new_version[1], 'patch': new_version[2]}

def get_lib_designator(pkg_name: str):
    gz_match = re.match(r'gz-(.*)', pkg_name)
    if gz_match:
        return gz_match.group(1)
    elif pkg_name == 'sdformat':
        return 'sdformat'
    else:
        raise ValueError(f'Could not extract designator from pkg_name: "{pkg_name}"')

def stable_unique(items: list):
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items

def pkg_has_extra_cmake(pkg_name_no_version):
    return pkg_name_no_version not in ['gz-tools', 'gz-cmake']

def pkg_has_dsv(pkg_name_no_version):
    return pkg_name_no_version not in ['gz-tools', 'gz-cmake']

def pkg_has_patches(pkg_name_no_version):
    return pkg_name_no_version in ['gz-cmake', 'gz-rendering']

def pkg_has_swig(pkg_name_no_version):
    return pkg_name_no_version in ['gz-math']

def pkg_has_pybind11(pkg_name_no_version):
    return pkg_name_no_version in ['gz-math', 'sdformat', 'gz-transport', 'gz-sim']

def pkg_has_docs(pkg_name_no_version):
    return pkg_name_no_version not in ['sdformat']

def cmake_pkg_name(pkg_name_no_version):
    # gz-fuel-tools needs special care as it's cmake package name is different
    # from its deb package name.
    if pkg_name_no_version == 'gz-fuel-tools':
        return 'gz-fuel_tools'
    return pkg_name_no_version


def create_vendor_package_xml(src_pkg_xml: Package, existing_package: Package | None):
    templates_path = Path(__file__).resolve().parent / "templates"
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path),
                                   trim_blocks=True, lstrip_blocks=True,
                                   keep_trailing_newline=True)
    template = jinja_env.get_template("package.xml.jinja")
    params = {}
    vendor_pkg_xml = copy.deepcopy(src_pkg_xml)

    params['pkg'] = vendor_pkg_xml

    pkg_name_no_version = remove_version(vendor_pkg_xml.name)
    params['vendor_name'] = create_vendor_name(pkg_name_no_version)

    # The gazebo dependencies need to be vendored and we need to use `<depend>`
    # on each dependency regardless of whether it's a build or exec dependency
    gz_build_deps, vendor_pkg_xml.build_depends = separate_gz_deps(vendor_pkg_xml.build_depends)
    gz_exec_deps, vendor_pkg_xml.exec_depends = separate_gz_deps(vendor_pkg_xml.exec_depends)
    gz_test_deps, vendor_pkg_xml.test_depends = separate_gz_deps(vendor_pkg_xml.test_depends)
    gz_doc_deps, vendor_pkg_xml.doc_depends = separate_gz_deps(vendor_pkg_xml.doc_depends)

    gz_deps = stable_unique(gz_build_deps + gz_exec_deps + gz_test_deps + gz_doc_deps)

    for dep in gz_deps:
        vendorize_gz_dependency(dep)

    params['gz_vendor_deps'] = gz_deps

    params['vendor_pkg_version'] = existing_package.version if existing_package is not None else "0.0.1"

    return template.render(params)

def create_cmake_file(src_pkg_xml: Package):
    templates_path = Path(__file__).resolve().parent / "templates"
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path),
                                   trim_blocks=True, lstrip_blocks=True,
                                   keep_trailing_newline=True)
    template = jinja_env.get_template("CMakeLists.txt.jinja")
    params = {}
    vendor_pkg_xml = copy.deepcopy(src_pkg_xml)
    params['pkg'] = vendor_pkg_xml

    pkg_name_no_version = remove_version(vendor_pkg_xml.name)
    params['github_pkg_name'] = pkg_name_no_version
    params['vendor_name'] = create_vendor_name(pkg_name_no_version)
    params['cmake_pkg_name']=cmake_pkg_name(pkg_name_no_version)

    # The gazebo dependencies need to be vendored and we need to use `<depend>`
    # on each dependency regardless of whether it's a build or exec dependency
    gz_build_deps, _ = separate_gz_deps(vendor_pkg_xml.build_depends)
    gz_exec_deps, _ = separate_gz_deps(vendor_pkg_xml.exec_depends)
    gz_test_deps, _ = separate_gz_deps(vendor_pkg_xml.test_depends)
    gz_doc_deps, _ = separate_gz_deps(vendor_pkg_xml.doc_depends)

    params['gz_vendor_deps'] = stable_unique(gz_build_deps + gz_exec_deps + gz_test_deps + gz_doc_deps)

    for dep in params['gz_vendor_deps']:
        vendorize_gz_dependency(dep)

    params['vendor_has_extra_cmake'] = pkg_has_extra_cmake(pkg_name_no_version)
    params['vendor_has_dsv'] = pkg_has_dsv(pkg_name_no_version)
    params['has_patches'] = pkg_has_patches(pkg_name_no_version)
    params['version']=split_version(vendor_pkg_xml.version)

    params['cmake_args'] = []
    if pkg_has_docs(pkg_name_no_version):
        params['cmake_args'] = ['-DBUILD_DOCS:BOOL=OFF']

    if pkg_has_pybind11(pkg_name_no_version):
        params['cmake_args'].append('-DSKIP_PYBIND11:BOOL=ON')
    if pkg_has_swig(pkg_name_no_version):
        params['cmake_args'].append('-DSKIP_SWIG:BOOL=ON')
    return template.render(params)

def generate_vendor_package_files(package: Package, existing_package: Package | None, output_dir):
    filtered_package = filter_dependencies(package)
    output_package_xml = create_vendor_package_xml(filtered_package , existing_package)
    output_cmake = create_cmake_file(filtered_package)
    if output_dir :
        with open(Path(output_dir) / "package.xml", 'w') as f:
            f.write(output_package_xml)
        with open(Path(output_dir) / "CMakeLists.txt", 'w') as f:
            f.write(output_cmake)
    else:
        print(output_package_xml)
        print(output_cmake)

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Parse package.xml file and generate a vendor package',
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        help='Output directory',
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

    if not args.output_dir:
        args.output_dir = vendor_name

    try:
        os.mkdir(args.output_dir)
    except FileExistsError:
        pass

    existing_package_path = Path(args.output_dir) / "package.xml"
    try:
        existing_package = parse_package(existing_package_path)
    except InvalidPackage as e:
        print(f"Error parsing '{existing_package_path}")
        raise e

    generate_vendor_package_files(package, existing_package, args.output_dir)

    templates_path = Path(__file__).resolve().parent / "templates"
    # Copy other files
    for file in ["LICENSE", "CONTRIBUTING.md"]:
        shutil.copy(templates_path / file, Path(args.output_dir) / file)

    shutil.copy(templates_path / "config.cmake.in", Path(args.output_dir) / f"{cmake_pkg_name(pkg_name_no_version)}-config.cmake.in")
    shutil.copy(templates_path / "extras.cmake.in", Path(args.output_dir) / f"{vendor_name}-extras.cmake.in")

    if pkg_has_dsv(pkg_name_no_version):
        shutil.copy(templates_path / "vendor.dsv.in", Path(args.output_dir) / f"{vendor_name}.dsv.in")

if __name__ == "__main__":
    main()
