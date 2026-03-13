load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_python//python:defs.bzl", "py_library")
load("@rules_python//python:defs.bzl", "py_test")
load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")
load("@rules_oci//oci:defs.bzl", "oci_image", "oci_load")

# client backend 
py_library(
    name = "client_lib",
    srcs = ["src/client.py"],
    imports = ["src"],
    deps = [
        requirement("requests"),
    ]
)
py_binary(
    name = "client_app",
    srcs = ["src/client.py"],
    main = "src/client.py",
    deps = [
        requirement("requests")
    ]
)

# dockerized backend image 
pkg_tar(
    name = "backend_layer",
    srcs = [":client_app"],
    include_runfiles = True,
    package_dir = "/",
    strip_prefix = "Python",
)

oci_image(
    name = "backend_image",
    base = "@distroless_python",
    tars = [":backend_layer"],
    entrypoint = ["/Python/client_app"],
)

oci_load(
    name = "tarball",
    image = ":backend_image",
    repo_tags = ["trading-backend:latest"],
)

# frontend 
py_library(
    name = "graph",
    srcs = ["src/graph.py"],
    imports = ["src"],
    deps = [
        requirement("pandas"),
        requirement("plotly")
    ]
)

py_binary(
    name = "viewer",
    srcs = ["src/main.py"],
    main = "src/main.py",
    deps = [
        ":graph",
        requirement("requests"),
        requirement("plotly")
    ]
)

# tests 
py_test(
    name = "split_test",
    srcs = ["test/test-graph.py"],
    main = "test/test-graph.py",
    imports = ["src"],
    deps = [
        ":graph"
    ]
)

# platform selection to prevent linux <> mac compatibility issues
platform(
    name = "linux_arm64",
    constraint_values = [
        "@platforms//os:linux",
        "@platforms//cpu:aarch64",
    ],
)