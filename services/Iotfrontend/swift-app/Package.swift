// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "SwiftApp",
    platforms: [
        .macOS(.v12)
    ],
    products: [
        .executable(name: "App", targets: ["App"])
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-nio.git", from: "2.32.0"),
    ],
    targets: [
        .executableTarget(
            name: "App",
            dependencies: [
                .product(name: "NIO", package: "swift-nio"),
                .product(name: "NIOHTTP1", package: "swift-nio"),
            ]
        )
    ]
)
