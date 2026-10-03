// swift-tools-version: 6.4
// The swift-tools-version declares the minimum version of Swift required to build this package.

import FoundationEssentials
import PackageDescription

let THORVG_LOCAL_BUNDLE_PATH: String? = "artifacts/thorvg-v1.1.2-linux-x86_64.artifactbundle/"

let thorVGNativeTarget: Target =
    if let THORVG_LOCAL_BUNDLE_PATH {
        .binaryTarget(
            name: "ThorVGNative",
            path: THORVG_LOCAL_BUNDLE_PATH
        )
    } else {
        .binaryTarget(
            name: "ThorVGNative",
            url:
                "https://github.com/ongsalt/swift-thorvg/releases/download/v1.1.2/thorvg-v1.1.2.artifactbundleindex",
            checksum: "17f2e2a9c363c9d82ba8e6fdd3b657e5d43f03d9019a1a2c199bfdb205498291",
        )
    }

let package = Package(
    name: "swift-thorvg",
    products: [
        .library(
            name: "swift-thorvg",
            targets: ["swift_thorvg"]
        )
    ],
    targets: [
        thorVGNativeTarget,
        .target(
            name: "swift_thorvg",
            dependencies: [
                "ThorVGNative"
            ],
            swiftSettings: [
                .enableUpcomingFeature("ApproachableConcurrency"),
            ],
        ),
        .testTarget(
            name: "swift_thorvgTests",
            dependencies: ["swift_thorvg"],
            swiftSettings: [
                .enableUpcomingFeature("ApproachableConcurrency")
            ],
        ),
    ]
)
