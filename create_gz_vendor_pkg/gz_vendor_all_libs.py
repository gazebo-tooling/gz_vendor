import argparse
from os.path import expanduser
import sys
from urllib.request import urlopen
import tempfile
import yaml
import create_vendor_package
from pathlib import Path
from subprocess import run


def clone(path, info):
    run(["git", "clone", "--depth", "1", "-b", info["version"], info["url"], path])


def get_collection(release):
    collection_url = f"https://github.com/gazebo-tooling/gazebodistro/raw/master/collection-{release}.yaml"  # noqa
    collection_yaml = urlopen(url=collection_url)
    return yaml.full_load(collection_yaml)


def get_collection_local(release):
    with open(expanduser(f"~/ws/{release}/src/collection-{release}.yaml"), "r") as f:
        return yaml.full_load(f.read())


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Update all packages for a given Gazebo release",
    )

    parser.add_argument(
        "gazebo_release",
        type=str,
        help="Name of Gazebo release to use",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Output directory",
    )
    args, unknown_args = parser.parse_known_args(argv)
    collection = get_collection_local(args.gazebo_release)

    # Sparse clone all the repos first
    with tempfile.TemporaryDirectory(prefix="gz_vendor_") as libs_path:
        for name, info in collection["repositories"].items():
            lib_path = Path(libs_path) / name
            clone(lib_path, info)

            package_xml_path = Path(lib_path) / "package.xml"
            print(package_xml_path)

            output_dir_args = []
            if args.output_dir != "":
                vendor_name = name.replace('-', '_') + '_vendor'
                output_path = str(Path(args.output_dir) / vendor_name)
                output_dir_args.append("--output_dir")
                output_dir_args.append(output_path)

            try:
                create_vendor_package.main([str(package_xml_path), *output_dir_args, *unknown_args])
            except Exception as e:
                print("Error: ", e)
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
