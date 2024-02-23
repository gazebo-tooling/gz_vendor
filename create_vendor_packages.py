import argparse
import sys
from catkin_pkg.package import Dependency, parse_package_string, Package
import re
import jinja2

VENDOR_PKG_TEMPLATE = '''\
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>{{ vendor_name }}</name>
  <version>{{ pkg.version }}</version>
  <description>{{ pkg.description }}</description>
  {% for maintainer in pkg.maintainers %}
  <maintainer email="{{ maintainer.email }}">{{ maintainer.name }}</maintainer>
  {% endfor %}
  {% for license in pkg.licenses %}
  <license>{{ license }}</license>
  {% endfor %}
  {% for url in pkg.urls %}
  <url type="{{ url.type }}">{{ url.url }}</url>
  {% endfor %}
  {% for author in pkg.authors %}
  <author email="{{ author.email }}">{{ author.name }}</author>
  {% endfor %}

  <buildtool_depend>ament_cmake_core</buildtool_depend>
  <buildtool_depend>ament_cmake_test</buildtool_depend>
  <buildtool_depend>ament_cmake_vendor_package</buildtool_depend>

  {% for dep in pkg.build_depends %}
  <build_depend>{{ dep.name }}</build_depend>
  {% endfor %}
  {% for dep in pkg.exec_depends %}
  <exec_depend>{{ dep.name }}</exec_depend>
  {% endfor %}
  {% for dep in pkg.test_depends %}
  <test_depend>{{ dep.name }}</test_depend>
  {% endfor %}
  {% for dep in pkg.doc_depends %}
  <doc_depend>{{ dep.name }}</doc_depend>
  {% endfor %}
  {% for dep in gz_vendor_deps %}
  <depend>{{ dep.name }}</depend>
  {% endfor %}

  <!-- Depend on the package we are vendoring to allow building it from source -->
  <build_depend condition="$GZ_BUILD_FROM_SOURCE != ''">{{ pkg.name }}</build_depend>

  <test_depend>ament_cmake_copyright</test_depend>
  <test_depend>ament_cmake_lint_cmake</test_depend>
  <test_depend>ament_cmake_xmllint</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
'''


GZ_LIBRARIES = [
    'gz-cmake',
    'gz-tools',
    'gz-utils',
    'gz-math',
    'gz-common',
    'gz-plugin'
    'gz-msgs'
    'gz-transport',
    'gz-physics',
    'gz-rendering',
    'gz-sensors',
    'gz-gui',
    'gz-sim',
    'gz-launch'
    'sdformat',
]

def remove_version(pkg_name: str):
    pkg_name_no_version = re.search('[-_a-z]*', pkg_name)
    if not pkg_name_no_version:
        raise RuntimeError("Could not parse package name")
    return pkg_name_no_version.group(0)

def create_vendor_name(pkg_name: str):
    return f"{pkg_name.replace('-', '_')}_vendor"

def is_gz_library(dep: Dependency):
    pkg_name_no_version = remove_version(dep.name)
    return pkg_name_no_version in GZ_LIBRARIES

def vendorize_gz_dependency(dep: Dependency):
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

def create_vendor_package_xml(src_pkg_xml: Package):
    jinja_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
    template = jinja_env.from_string(VENDOR_PKG_TEMPLATE)

    pkg_name_no_version = remove_version(src_pkg_xml.name)
    vendor_name = create_vendor_name(pkg_name_no_version)

    # The gazebo dependencies need to be vendored and we need to use `<depend>`
    # on each dependency regardless of whether it's a build or exec dependency
    gz_build_deps, src_pkg_xml.build_depends = separate_gz_deps(src_pkg_xml.build_depends)
    gz_exec_deps, src_pkg_xml.exec_depends = separate_gz_deps(src_pkg_xml.exec_depends)
    gz_test_deps, src_pkg_xml.test_depends = separate_gz_deps(src_pkg_xml.test_depends)
    gz_doc_deps, src_pkg_xml.doc_depends = separate_gz_deps(src_pkg_xml.doc_depends)

    gz_deps = set(gz_build_deps + gz_exec_deps + gz_test_deps + gz_doc_deps)
    for dep in gz_deps:
        vendorize_gz_dependency(dep)

    return template.render(pkg=src_pkg_xml, pkg_name_no_version=pkg_name_no_version,
                           vendor_name=vendor_name, gz_vendor_deps=gz_deps)

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Parse package.xml file and generate a vendor package',
    )
    parser.add_argument(
        'package_xml',
        type=argparse.FileType('r', encoding='utf-8'),
        help='The path to a package.xml file',
    )
    args = parser.parse_args(argv)
    try:
        package = parse_package_string(
            args.package_xml.read(), filename=args.package_xml.name)
    except Exception as e:
        print("Error parsing '%s':" % args.package_xml.name, file=sys.stderr)
        raise e
    finally:
        args.package_xml.close()
    print(create_vendor_package_xml(package))

if __name__ == "__main__":
    main()
