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
    target = f"{platform}-{os.environ['ARCH']}"
    bundle = artifacts / f"thorvg-{tag}-{target}.artifactbundle"

    pattern = "*thorvg*.lib" if platform == "windows" else "libthorvg*.a"
    library = next(Path("thorvg/build/src").glob(pattern))

    shutil.copytree("Bridge/include", bundle / "include", dirs_exist_ok=True)
    shutil.copy2(library, bundle / library.name)
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
    (bundle / "info.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    
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
    (artifacts / f"thorvg-{tag}.artifactbundleindex").write_text(
        json.dumps(index, indent=2) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    if "--index" in sys.argv:
        create_artifact_bundle_index()
    else:
        create_artifact_bundle()
