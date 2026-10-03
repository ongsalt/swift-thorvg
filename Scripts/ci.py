import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


tag = os.environ["TAG"]
artifacts = Path("artifacts")
supported_triples = {
    "linux-x86_64": "x86_64-unknown-linux-gnu",
    "linux-arm64": "arm64-unknown-linux-gnu",
    "windows-x86_64": "x86_64-unknown-windows-msvc",
    "windows-arm64": "arm64-unknown-windows-msvc",
}


def create_artifact_bundle():
    platform = os.environ["PLATFORM"].lower()
    arch = os.environ['ARCH']
    target = f"{platform}-{arch}"

    bundle = artifacts / f"thorvg-{tag}-{target}.artifactbundle"

    library = Path("thorvg/build/src/libthorvg-1.a")

    shutil.copytree("Bridge/include", bundle / "include", dirs_exist_ok=True)
    shutil.copy2(library, bundle / library.name)

    # dont link libm on windows
    if platform == "windows":
        module_map = bundle / "include/module.modulemap"
        module_map.write_text(
            module_map.read_text(encoding="utf-8").replace(' link "m"\n', ""),
            encoding="utf-8",
        )

    info = {
        "schemaVersion": "1.0",
        "artifacts": {
            "ThorVGNative": {
                "type": "staticLibrary",
                "version": tag.removeprefix("v"),
                "variants": [{
                    "path": library.name,
                    "supportedTriples": [supported_triples[target]],
                    "staticLibraryMetadata": {
                        "headerPaths": ["include"],
                        "moduleMapPath": "include/module.modulemap",
                    },
                }],
            },
        },
    }
    info_path = bundle / "info.json"
    info_path.write_text(json.dumps(info) + "\n", encoding="utf-8")
    
    shutil.make_archive(str(bundle), "zip", root_dir=artifacts, base_dir=bundle.name)


def create_artifact_bundle_index():
    archives = []
    for target, triple in supported_triples.items():
        archive = artifacts / f"thorvg-{tag}-{target}.artifactbundle.zip"
        archives.append({
            "fileName": archive.name,
            "checksum": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "supportedTriples": [triple],
        })
        
    index = {"schemaVersion": "1.0", "archives": archives}
    index_path = artifacts / f"thorvg-{tag}.artifactbundleindex"
    index_path.write_text(json.dumps(index) + "\n", encoding="utf-8",)


if __name__ == "__main__":
    if "--index" in sys.argv:
        create_artifact_bundle_index()
    else:
        create_artifact_bundle()
