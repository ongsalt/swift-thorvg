import shutil
import os
from pathlib import Path
import json

tag = os.environ["TAG"]
platform = os.environ["PLATFORM"].lower()
# arch = os.environ["ARCH"]
arch = "x86_64"

target = f"{platform}-{arch}"

supported_triples = {
    "linux-x86_64" : "x86_64-unknown-linux-gnu"
}

def create_info_json():
    version = tag[1:]
    content = {
        "schemaVersion": "1.0",
        "artifacts": {
            "ThorVGNative": {
                "type": "staticLibrary",
                "version": version,
                "variants": [{
                    "path": "libthorvg.a",
                    "supportedTriples": [supported_triples[target]],
                    "staticLibraryMetadata": {
                        "headerPaths": ["include"],
                        "moduleMapPath": "include/module.modulemap"
                    }
                }]
            }
        }
    }

    with open("bundle/info.json", "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)


def create_artifact_bundle():
    Path("bundle").mkdir()
    create_info_json()

    shutil.copytree("Bridge/include", "bundle/include")

    shutil.copy2("thorvg/build/src/libthorvg-1.a", "bundle/")

    shutil.make_archive(f"artifacts/thorvg-{tag}-{target}.artifactbundle", "zip", root_dir=".", base_dir="bundle")

create_artifact_bundle()