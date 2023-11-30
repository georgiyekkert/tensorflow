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

# Bazel rule for collecting the py files that a target depends on.
def _transitive_py_impl(ctx):
    outputs = _get_transitive_py_deps([], ctx.attr.deps)

    #print(outputs)
    return DefaultInfo(files = outputs)

_transitive_py = rule(
    attrs = {
        "deps": attr.label_list(
            allow_files = True,
            providers = [PyInfo],
        ),
    },
    implementation = _transitive_py_impl,
)

def transitive_py_deps(name, deps = [], **kwargs):
    _transitive_py(name = name + "_gather", deps = deps)
    native.filegroup(name = name, srcs = [":" + name + "_gather"])

def _get_transitive_py_deps(src, deps):
    """Obtain the py files for a target and its transitive dependencies.

      Args:
        src: a list of py files
        deps: a list of targets that are direct dependencies

      Returns:
        a collection of the transitive headers
      """
    return depset(
        src,
        transitive = [dep[PyInfo].transitive_sources for dep in deps],
    )