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
"""Rule to collect output group info files."""

def _output_deps_impl(ctx):
    srcs = []
    for i in ctx.attr.deps:
        temp = []

        # we only need selected extensions
        extenstions = [".so", ".pyd", ".pyi", ".dll", ".dylib", ".lib", ".pd"]
        for s in i[OutputGroupInfo]._hidden_top_level_INTERNAL_.to_list():
            if "_solib" in s.dirname:
                continue
            if not any([s.basename.endswith(ext) for ext in extenstions]):
                continue
            if s.basename.startswith("libtensorflow"):
                continue
            temp.append(s)
        srcs.extend(temp)
    return DefaultInfo(files = depset(
        srcs,
    ))

_output_deps = rule(
    attrs = {
        "deps": attr.label_list(
            allow_files = True,
            providers = [OutputGroupInfo],
        ),
    },
    implementation = _output_deps_impl,
)

def output_group_deps(name, deps = []):
    _output_deps(name = name + "_gather", deps = deps)
    native.filegroup(name = name, srcs = [":" + name + "_gather"])
