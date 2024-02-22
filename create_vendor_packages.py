import argparse
import sys
from catkin_pkg.package import parse_package_string, Package
import re
import jinja2

VENDOR_PKG_TEMPLATE = '''
<?xml version="1.0"?>
<package format="3">
  <name>{{ name }}</name>
  <version>{{ pkg.version }}</version>
  <description>{{ pkg.description }}</description>
  {% for maintainer in pkg.maintainers %}
  <maintainer email="{{ maintainer.email }}">{{ maintainer.name }}</maintainer>
  {% endfor %}

  {% for license in pkg.licenses %}
  <license>{{ license }}<license>
  {% endfor %}

  {% for url in pkg.urls %}
  <url type="{{ url.type }}">{{ url.url }}</url>
  {% endfor %}

  {% for author in pkg.authors %}
  <author email="{{ author.email }}">{{ author.name }}</author>
  {% endfor %}

  {% for dep in pkg.build_depends %}
  <depend>{{ dep.name }}</depend>
  {% endfor %}
</package>
'''

def create_vendor_package_xml(src_pkg_xml: Package):
    jinja_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
    template = jinja_env.from_string(VENDOR_PKG_TEMPLATE)
    # Remove version number from the package name
    pkg_name_no_version = re.search('[-_a-z]*', src_pkg_xml.name)
    if not pkg_name_no_version:
        raise RuntimeError("Could not parse package name")

    print(template.render(pkg=src_pkg_xml, name="{pkg_name_no_version.group(0)}"))

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
    create_vendor_package_xml(package)

if __name__ == "__main__":
    main()
