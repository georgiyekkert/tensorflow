# Copyright 2023 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Bazel rule for collecting the header files that a target depends on.
def _transitive_hdrs_impl(ctx):
    outputs = _get_transitive_py_deps([], ctx.attr.deps)
    #print(outputs)
    return DefaultInfo(files = outputs)

_transitive_hdrs = rule(
    attrs = {
        "deps": attr.label_list(
            allow_files = True,
            providers = [PyInfo],
        ),
    },
    implementation = _transitive_hdrs_impl,
)

def transitive_py_deps(name, deps = [], **kwargs):
    _transitive_hdrs(name = name + "_gather", deps = deps)
    native.filegroup(name = name, srcs = [":" + name + "_gather"])

def _get_transitive_py_deps(src, deps):
    """Obtain the header files for a target and its transitive dependencies.

      Args:
        src: a list of header files
        deps: a list of targets that are direct dependencies

      Returns:
        a collection of the transitive headers
      """
    return depset(
        src,
        transitive = [dep[PyInfo].transitive_sources for dep in deps],
    )

def _quote(filename, protect = "="):
    """Quote the filename, by escaping = by \\= and \\ by \\\\"""
    return filename.replace("\\", "\\\\").replace(protect, "\\" + protect)

def dest_path(file):
    ret = file.short_path
    return ret


def _tf_wheel_impl(ctx):
    executable = ctx.executable.wheel_binary
    output_wheel = ctx.outputs.wheel

    args = ctx.actions.args()
    args.add("--output-name", output_wheel.path)

    deps = ctx.files.deps[:]
    for f in deps:
        args.add("--deps=%s" % (f.path))

    headers = ctx.files.headers[:]
    for f in headers:
        args.add("--headers=%s" % (f.path))

    xla_aot = ctx.files.xla_aot_compiled[:]
    for f in xla_aot:
        args.add("--xla_aot=%s" % (f.path))

    srcs = []
    for src in ctx.attr.srcs:
        for f in src.files.to_list():
            srcs.append(f)
            args.add("--srcs=%s" % (f.path))

    args.set_param_file_format("flag_per_line")
    args.use_param_file("@%s", use_always = False)
    ctx.actions.run(
        arguments = [args],
        inputs = srcs+deps+headers,
        outputs = [output_wheel],
        executable = executable,
    )

tf_wheel = rule(
    attrs = {
        "srcs": attr.label_list(allow_files = True),
        "deps": attr.label_list(allow_files = True),
        "headers": attr.label_list(allow_files = True),
        "xla_aot_compiled": attr.label_list(allow_files = True),
        "py_version": attr.string(),
        "platform": attr.string(),
        "tf_version": attr.string(),
        "wheel_binary": attr.label(
            default = Label("//tensorflow/tools/pip_package:build_pip_package_py"),
            executable = True,
            cfg = "host",
        ),
    },
    outputs = {
        "wheel": "tensorflow-%{tf_version}-cp%{py_version}-cp%{py_version}-%{platform}.whl",
    },
    implementation = _tf_wheel_impl,
)
