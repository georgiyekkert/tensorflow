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

def _transitive_cc_deps_impl(ctx):
    srcs = []
    for i in ctx.attr.deps:
        temp = []
        extenstions = [".so", ".pyd", ".pyi", ".dll", ".dylib", ".lib", ".pd"]
        for s in i[OutputGroupInfo]._hidden_top_level_INTERNAL_.to_list():
            if "_solib_k8/" in s.dirname:
                continue
            if not any([s.basename.endswith(ext) for ext in extenstions]):
              continue
            if s.basename.startswith("libtensorflow_S"):
                continue
            #if s.dirname.startswith("bazel-out/k8-opt/bin/_solib_k8/"):
            #    continue
            #if s.dirname.startswith("external/pypi"):
            #    continue
            #if s.basename.startswith("_solib_k8/"):
            #    continue
            #if not s.basename.endswith(".so") and not s.basename.endswith(".pyi") and not s.basename.endswith(".pyd"):
            #    continue
            #if s.basename.startswith("libtensorflow_Spython_"):
            #    continue
            temp.append(s)
        srcs.extend(temp)
    return DefaultInfo(files=depset(
        srcs,
    ))

_transitive_cc = rule(
    attrs = {
        "deps": attr.label_list(
            allow_files = True,
            providers = [OutputGroupInfo],
        ),
    },
    implementation = _transitive_cc_deps_impl,
)

def transitive_cc_deps(name, deps = [], **kwargs):
    _transitive_cc(name = name + "_gather", deps = deps)
    native.filegroup(name = name, srcs = [":" + name + "_gather"])

def _get_transitive_cc_deps(src, deps):
    """Obtain the header files for a target and its transitive dependencies.

      Args:
        src: a list of header files
        deps: a list of targets that are direct dependencies

      Returns:
        a collection of the transitive headers
      """
    return depset(
        src,
        transitive = [dep[OutputGroupInfo]._hidden_top_level_INTERNAL_ for dep in deps],
    )
