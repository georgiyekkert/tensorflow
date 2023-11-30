# Description:
#  Tools for building the TensorFlow pip package.

load("@local_config_cuda//cuda:build_defs.bzl", "if_cuda")
load("@local_config_syslibs//:build_defs.bzl", "if_not_system_lib")
load("//tensorflow:tensorflow.bzl", "filegroup_as_file", "transitive_hdrs")
load("//tensorflow/core/platform:build_config_root.bzl", "tf_additional_license_deps")
load("//third_party/mkl:build_defs.bzl", "if_enable_mkl", "if_mkl", "if_mkl_ml")
load("//tensorflow/tools/pip_package/utils:tf_wheel.bzl", "tf_wheel")
load("@python_version_repo//:py_version.bzl", "HERMETIC_PYTHON_VERSION")
load("//tensorflow:tensorflow.bzl", "VERSION")
load("@python//:defs.bzl", "host_platform")
load("//tensorflow/tools/pip_package/utils:py_deps.bzl", "transitive_py_deps")
load("//tensorflow/tools/pip_package/utils:cc_deps.bzl", "transitive_cc_deps")

package(default_visibility = ["//visibility:private"])

# This returns a list of headers of all public header libraries (e.g.,
# framework, lib), and all of the transitive dependencies of those
# public headers.  Not all of the headers returned by the filegroup
# are public (e.g., internal headers that are included by public
# headers), but the internal headers need to be packaged in the
# pip_package for the public headers to be properly included.
#
# Public headers are therefore defined by those that are both:
#
# 1) "publicly visible" as defined by bazel
# 2) Have documentation.
#
# This matches the policy of "public" for our python API.
transitive_hdrs(
    name = "included_headers",
    deps = [
        "//tensorflow/compiler/tf2xla:xla_compiled_cpu_function",
        "//tensorflow/compiler/mlir:mlir_graph_optimization_pass",
        "//tensorflow/core:core_cpu",
        "//tensorflow/core:framework",
        "//tensorflow/core:lib",
        "//tensorflow/core:protos_all_cc",
        "//tensorflow/core/platform:stream_executor",
        "//tensorflow/cc/saved_model:loader",
        "//tensorflow/cc/saved_model:reader",
        "//tensorflow/cc/saved_model:bundle_v2",
        "//tensorflow/c/experimental/filesystem:filesystem_interface",
        "//tensorflow/c/experimental/next_pluggable_device:c_api_hdrs",
        "//tensorflow/c/experimental/pluggable_profiler:pluggable_profiler_hdrs",
        "//tensorflow/c/experimental/stream_executor:stream_executor_hdrs",
        "//tensorflow/c/experimental/grappler:grappler_hdrs",
        "//tensorflow/c:kernels_hdrs",
        "//tensorflow/c:ops_hdrs",
        "@local_xla//xla/pjrt/c:pjrt_c_api_hdrs",
        "//tensorflow/core/common_runtime/next_pluggable_device/c:plugin_c_api_hdrs",
        # TODO(rostam): Revisit these after cc_shared_library everywhere
        "//tensorflow/cc:client_session",
        "//tensorflow/cc:cc_ops",
        # WARNING: None of the C/C++ code under python/ has any API guarantees, and TF team
        # reserves the right to change APIs and other header-level interfaces.  If your custom
        # op uses these headers, it may break when users upgrade their version of tensorflow.
        # NOTE(ebrevdo): None of the python symbols are exported by libtensorflow_framework.so.
        # Code that relies on these headers should dynamically link to
        # _pywrap_tensorflow_internal.so as well.
        "//tensorflow/python/grappler:model_analyzer_lib",
        "//tensorflow/python/lib/core:py_exception_registry",
        "//tensorflow/python/lib/core:pybind11_proto",
        "//tensorflow/python/lib/core:pybind11_absl",
        "//tensorflow/python/lib/core:pybind11_lib",
        "//tensorflow/python/lib/core:pybind11_status",
        "//tensorflow/python/lib/core:py_func_lib",
        "//tensorflow/python/lib/core:py_seq_tensor",
        "//tensorflow/python/lib/core:py_util",
        "//tensorflow/python/util:cpp_python_util",
        "//tensorflow/python/util:kernel_registry",
        "//tensorflow/python/framework:python_op_gen",
        "//tensorflow/python/client:tf_session_helper",
        "//third_party/eigen3",
        "@local_xla//xla/stream_executor",
    ] + if_cuda([
        "@local_config_cuda//cuda:cuda_headers",
    ]),
)

py_binary(
    name = "simple_console",
    srcs = ["simple_console.py"],
    srcs_version = "PY3",
    deps = ["//tensorflow:tensorflow_py"],
)

filegroup_as_file(
    name = "xla_compiled_cpu_runtime_srcs.txt",
    dep = "//tensorflow/compiler/tf2xla:xla_compiled_cpu_runtime_srcs",
)

filegroup(
    name = "xla_cmake",
    srcs = ["xla_build/CMakeLists.txt"],
)

# Add dynamic kernel dso files here.
DYNAMIC_LOADED_KERNELS = [
    "//tensorflow/core/kernels:libtfkernel_sobol_op.so",
]

PIP_DATA = [
    "licenses",
    "setup.py",
    "MANIFEST.in",
    "README",
    ":included_headers",
    ":xla_compiled_cpu_runtime_srcs.txt_file",
    ":xla_cmake",
    "//tensorflow/core:protos_all_proto_srcs",
    "//tensorflow/python/framework:meta_graph_testdata",
    "//tensorflow/python/kernel_tests/linalg/testdata:self_adjoint_eig_op_test_files",
]

COMMON_PIP_DEPS = [
    "//tensorflow/compiler/mlir/stablehlo:stablehlo",
    "//tensorflow/compiler/mlir/tensorflow:gen_mlir_passthrough_op_py",
    "//tensorflow/core/function/trace_type:serialization_test_proto_py",
    "//tensorflow/core/function/trace_type:serialization",
    #"//tensorflow/core:protos_all_proto_srcs",
    "//tensorflow/dtensor/python/tests:multi_client_test_util",
    "//tensorflow/dtensor/python/tests:test_util",
    "//tensorflow/lite/python:tflite_convert",
    "//tensorflow/lite/toco/python:toco_from_protos",
    "//tensorflow/lite/tools:visualize",
    "//tensorflow/python/autograph/core:test_lib",
    "//tensorflow/python/autograph/impl/testing:pybind_for_testing",
    "//tensorflow/python/autograph/pyct/testing:basic_definitions",
    "//tensorflow/python/autograph/pyct/testing:decorators",
    "//tensorflow/python/autograph/pyct/common_transformers:common_transformers",
    "//tensorflow/python/autograph/pyct/static_analysis:type_inference",
    "//tensorflow/python/autograph/utils:context_managers",
    "//tensorflow/python/autograph/utils:tensor_list",
    "//tensorflow/python/compiler:compiler",
    "//tensorflow/python/ops:cond_v2",
    "//tensorflow/python:distributed_framework_test_lib",
    "//tensorflow/python/distribute:distribute_test_lib_pip",
    "//tensorflow/python/training/experimental:loss_scale",
    "//tensorflow/python/training/experimental:loss_scale_optimizer",
    #"//tensorflow/python/framework:meta_graph_testdata",
    "//tensorflow/python/data/benchmarks:benchmark_base",
    "//tensorflow/python/data/experimental/kernel_tests/service:multi_process_cluster",
    "//tensorflow/python/data/experimental/kernel_tests/service:test_base",
    "//tensorflow/python/data/experimental/ops:testing",
    "//tensorflow/python/data/experimental/service:server_lib",
    "//tensorflow/python/data/kernel_tests:checkpoint_test_base",
    "//tensorflow/python/data/kernel_tests:test_base",
    "//tensorflow/python/data/kernel_tests:tf_record_test_base",
    "//tensorflow/python/ops/ragged:ragged_tensor_test_ops",
    "//tensorflow/python/debug:debug_pip",
    "//tensorflow/python/distribute:combinations",
    "//tensorflow/python/distribute/coordinator:fault_tolerance_test_base",
    "//tensorflow/python/distribute/failure_handling:check_preemption_py",
    "//tensorflow/python/distribute/failure_handling:failure_handling_lib",
    "//tensorflow/python/distribute/failure_handling:failure_handling_util",
    "//tensorflow/python/distribute:multi_process_runner",
    "//tensorflow/python/eager:eager_pip",
    "//tensorflow/python/keras:combinations",
    "//tensorflow/python/keras/mixed_precision:test_util",
    "//tensorflow/python/keras/utils:dataset_creator",
    #"//tensorflow/python/kernel_tests/linalg/testdata:self_adjoint_eig_op_test_files",
    "//tensorflow/python/kernel_tests/nn_ops:bias_op_base",
    "//tensorflow/python/kernel_tests/nn_ops:cudnn_deterministic_base",
    "//tensorflow/python/kernel_tests/nn_ops:depthwise_conv_op_base",
    "//tensorflow/python/kernel_tests/nn_ops:xent_op_test_base",
    "//tensorflow/python/kernel_tests/random:util",
    "//tensorflow/python/kernel_tests/signal:test_util",
    "//tensorflow/python/kernel_tests/sparse_ops:sparse_xent_op_test_base",
    "//tensorflow/python/lib:__init__",
    "//tensorflow/python/ops/parallel_for:test_util",
    "//tensorflow/python/ops/structured:structured_tensor_dynamic",
    "//tensorflow/python/platform:resource_loader",
    "//tensorflow/python/profiler:trace",
    "//tensorflow/python/saved_model:saved_model",
    "//tensorflow/python/summary:__init__",
    "//tensorflow/python/summary:plugin_asset",
    "//tensorflow/python/summary:summary_iterator",
    "//tensorflow/python/summary:summary_py",
    "//tensorflow/python/tools:tools_pip",
    "//tensorflow/python/tools/api/generator:create_python_api",
    "//tensorflow/python/tools/api/generator2/extractor:extractor",
    "//tensorflow/python/tools/api/generator2/generator:generator",
    "//tensorflow/python/tpu",
    "//tensorflow/python/util:deprecated_module",
    "//tensorflow/python/util:deprecated_module_new",
    "//tensorflow/python/util:example_parser_configuration",
    "//tensorflow/python/util:function_utils",
    "//tensorflow/python/util:keyword_args",
    "//tensorflow/python/util:lock_util",
    "//tensorflow/python/util:module_wrapper",
    "//tensorflow/python/util:serialization",
    "//tensorflow/python/ops:image_grad_test_base",
    "//tensorflow/python/framework:memory_checker",
    "//tensorflow/python/framework:test_ops",
    "//tensorflow/python/ops:while_v2",
    "//tensorflow/tools/common:public_api",
    "//tensorflow/tools/common:test_module1",
    "//tensorflow/tools/common:traverse",
    "//tensorflow/tools/docs:tf_doctest_lib",
    "@local_tsl//tsl/profiler/protobuf:trace_events_proto_py",
    "//tensorflow/python/distribute:parameter_server_strategy_v2",
    "//tensorflow/python/distribute/coordinator:cluster_coordinator",
    "//tensorflow/python/distribute/coordinator:remote_eager_lib",
    "//tensorflow/python/distribute/coordinator:metric_utils",
    "//tensorflow/python/distribute/experimental/rpc:rpc_ops",
    "//tensorflow/python/util:pywrap_xla_ops",
    "//tensorflow/tools/compatibility:tf_upgrade_v2",
    "//tensorflow:tensorflow_py",
]

filegroup(
    name = "licenses",
    data = [
        "//:LICENSE",
        "//third_party/icu/data:LICENSE",
        "@com_google_absl//:LICENSE",
        "@com_google_protobuf//:LICENSE",
        "@curl//:COPYING",
        "@ducc//:LICENSE",
        "@flatbuffers//:LICENSE",
        "@gemmlowp//:LICENSE",
        "@libjpeg_turbo//:LICENSE.md",
        "@llvm-project//llvm:LICENSE.TXT",
        "@llvm-project//mlir:LICENSE.TXT",
        "@local_config_tensorrt//:LICENSE",
        "@ml_dtypes//:LICENSE",
        "@org_brotli//:LICENSE",
        "@pasta//:LICENSE",
        "@png//:LICENSE",
        "@ruy//:LICENSE",
        "@six_archive//:LICENSE",
        "@snappy//:COPYING",
        "@stablehlo//:LICENSE",
        "@tf_runtime//:LICENSE",
    ] + select({
        "//tensorflow:android": [],
        "//tensorflow:ios": [],
        "//tensorflow:linux_s390x": [],
        "//tensorflow:windows": [],
        "//conditions:default": [
            "@com_github_googlecloudplatform_google_cloud_cpp//:LICENSE",
        ],
    }) + select({
        "@local_tsl//tsl:with_numa_support": [
            "@hwloc//:COPYING",
        ],
        "//conditions:default": [],
    }) + if_cuda([
        "@cub_archive//:LICENSE.TXT",
        "@local_config_nccl//:LICENSE",
    ]) + if_mkl([
        "//third_party/mkl_dnn:LICENSE",
    ]) + if_enable_mkl(["//third_party/mkl:LICENSE"]) + if_not_system_lib(
        "absl_py",
        [
            "@absl_py//:LICENSE",
        ],
    ) + tf_additional_license_deps(),
)

sh_binary(
    name = "build_pip_package",
    srcs = ["build_pip_package.sh"],
    data = COMMON_PIP_DEPS +
           select({
               "//tensorflow:windows": [
                   "//tensorflow/python:pywrap_tensorflow_import_lib_file",
               ],
               "//conditions:default": [],
           }) +
           select({
               "//tensorflow:dynamic_loaded_kernels": DYNAMIC_LOADED_KERNELS,
               "//conditions:default": [],
           }) + if_mkl_ml(["//third_party/mkl:intel_binary_blob"]) + [
        "//tensorflow:tf_python_api_gen_v2",
    ],
    visibility = ["//visibility:public"],
)

SO_SRCS = [
    "//tensorflow:tensorflow_framework",
    "//tensorflow:tensorflow_cc",
]

GENERATED_SO = [
    #"//tensorflow/core/kernels:libtfkernel_sobol_op",  .so?
    "//tensorflow/python:flags_pybind",
    "//tensorflow/python:_pywrap_py_exception_registry",
    "//tensorflow/python:_pywrap_toco_api",
    "//tensorflow/python:_pywrap_tfcompile",
    "//tensorflow/python:_pywrap_tfe",
    "//tensorflow/python:_pywrap_sanitizers",
    "//tensorflow/python:_pywrap_parallel_device",
    "//tensorflow/python:_pywrap_quantize_training",
    "//tensorflow/compiler/mlir/quantization/tensorflow/python:pywrap_quantize_model",
    "//tensorflow/python:_pywrap_dtensor_device",
    "//tensorflow/python:_pywrap_mlir",
    "//tensorflow/python/autograph/impl/testing:pybind_for_testing",
    "//tensorflow/python/grappler:_pywrap_tf_cluster",
    "//tensorflow/python/grappler:_pywrap_tf_item",
    "//tensorflow/python/grappler:_pywrap_tf_optimizer",
    "//tensorflow/python/platform:_pywrap_stacktrace_handler",
    "//tensorflow/python/platform:_pywrap_cpu_feature_guard",
    "//tensorflow/python/platform:_pywrap_tf2",
    "//tensorflow/python/util:_pywrap_determinism",
    "//tensorflow/python/util:_tf_stack",
    "//tensorflow/python/util:_pywrap_nest",
    "//tensorflow/python/util:_pywrap_checkpoint_reader",
    "//tensorflow/python/util:fast_module_type",
    "//tensorflow/python/util:_pywrap_transform_graph",
    "//tensorflow/python/util:_pywrap_tfprof",
    "//tensorflow/python/util:_pywrap_util_port",
    "//tensorflow/python/util:_pywrap_stat_summarizer",
    "//tensorflow/python/util:_pywrap_utils",
    "//tensorflow/python/util:_pywrap_kernel_registry",
    "//tensorflow/python/util:_pywrap_tensor_float_32_execution",
    "//tensorflow/python/data/experimental/service:_pywrap_server_lib",
    "//tensorflow/python/data/experimental/service:_pywrap_snapshot_utils",
    "//tensorflow/python/data/experimental/service:_pywrap_utils",
    "//tensorflow/python/lib/core:_pywrap_py_func",
    "//tensorflow/python/lib/io:_pywrap_file_io",
    "//tensorflow/python/lib/io:_pywrap_record_io",
    "//tensorflow/python/framework:_test_metrics_util",
    "//tensorflow/python/framework:_pywrap_python_api_dispatcher",
    "//tensorflow/python/framework:_op_def_library_pybind",
    "//tensorflow/python/framework:_op_def_registry",
    "//tensorflow/python/framework:_pywrap_python_op_gen",
    "//tensorflow/python/framework:_pywrap_python_api_info",
    "//tensorflow/python/framework:_pywrap_python_api_parameter_converter",
    "//tensorflow/python/framework:_errors_test_helper",
    "//tensorflow/python/framework:_python_memory_checker_helper",
    "//tensorflow/python/framework:_dtypes",
    "//tensorflow/python/framework:fast_tensor_util",
    "//tensorflow/python/framework:_proto_comparators",
    "//tensorflow/python/saved_model:pywrap_saved_model",
    "//tensorflow/python/client:_pywrap_tf_session",
    "//tensorflow/python/client:_pywrap_events_writer",
    "//tensorflow/python/client:_pywrap_debug_events_writer",
    "//tensorflow/python/client:_pywrap_device_lib",
    "//tensorflow/python/profiler/internal:_pywrap_traceme",
    "//tensorflow/python/profiler/internal:_pywrap_profiler",
    "//tensorflow/compiler/tf2tensorrt:_pywrap_py_utils",
    "//tensorflow/compiler/mlir/stablehlo:stablehlo_extension",
    "//tensorflow/lite/python/interpreter_wrapper:_pywrap_tensorflow_interpreter_wrapper",
    "//tensorflow/lite/python/optimize:_pywrap_tensorflow_lite_calibration_wrapper",
    "//tensorflow/lite/python/metrics:_pywrap_tensorflow_lite_metrics_wrapper",
    "//tensorflow/lite/python/analyzer_wrapper:_pywrap_analyzer_wrapper",
    "//tensorflow/python/util:pywrap_xla_ops"
]

SO = [
    "//tensorflow/compiler/tf2xla/ops:_xla_ops.so",
    "//tensorflow/core/kernels:libtfkernel_sobol_op.so",
    "//tensorflow/lite/experimental/microfrontend:python/ops/_audio_microfrontend_op.so",
]

py_binary(
    name = "build_pip_package_py",
    srcs = [
        "build_pip_package.py",
    ],
    main = "build_pip_package.py",
    deps = [
        "@pypi_setuptools//:pkg",
        "@pypi_wheel//:pkg",
    ],
)

tf_wheel(
    name = "tensorflow",
    srcs = [
        ":cc_deps",
    ] + SO, # + SO_SRCS
    headers = [
        ":included_headers",
        "//tensorflow/core:protos_all_proto_srcs",
    ],
    platform = "linux_x86_64",
    py_version = HERMETIC_PYTHON_VERSION.replace(".", ""),
    tf_version = VERSION,
    xla_aot_compiled = [
        "//tensorflow/compiler/tf2xla:xla_compiled_cpu_runtime_srcs",
        ":xla_cmake",
    ],
    deps = [
        "MANIFEST.in",
        "THIRD_PARTY_NOTICES.txt",
        "setup.py",
        ":py_deps",
    ],
)

transitive_cc_deps(
    name = "cc_deps",
    deps = GENERATED_SO,
)

transitive_py_deps(
    name = "py_deps",
    deps = COMMON_PIP_DEPS,
)
