# Copyright 2023 The Tensorflow Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tool to rearrange files and build the wheel."""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from tensorflow.tools.pip_package.v2.utils.utils import copy_file
from tensorflow.tools.pip_package.v2.utils.utils import create_init_files
from tensorflow.tools.pip_package.v2.utils.utils import is_macos
from tensorflow.tools.pip_package.v2.utils.utils import is_windows
from tensorflow.tools.pip_package.v2.utils.utils import replace_inplace


def parse_args() -> argparse.Namespace:
  """Arguments parser."""
  parser = argparse.ArgumentParser(
      description="Helper for building pip package", fromfile_prefix_chars="@")
  parser.add_argument(
      "--output-name", required=True,
      help="Output file for the wheel, mandatory")
  parser.add_argument("--project-name", required=True,
                      help="Project name to be passed to setup.py")
  parser.add_argument(
      "--headers", help="header files for the wheel", action="append")
  parser.add_argument("--srcs", help="source files for the wheel",
                      action="append")
  parser.add_argument("--xla_aot", help="xla aot compiled sources",
                      action="append")
  parser.add_argument("--version", help="TF version")
  return parser.parse_args()


def prepare_headers(headers: list[str], srcs_dir: str) -> None:
  """Copy and rearrange header files in the source directory."""
  path_to_exclude = [
      "external/pypi",
      "external/jsoncpp_git/src",
      "local_config_cuda/cuda/_virtual_includes",
      "local_config_tensorrt",
      "python_x86_64",
      "python_aarch64",
      "llvm-project/llvm/",
  ]

  path_to_replace = {
      "external/com_google_absl/": "",
      "external/eigen_archive/": "",
      "external/jsoncpp_git/": "",
      "external/com_google_protobuf/src/": "",
      "external/local_xla/": "tensorflow/compiler",
      "external/local_tsl/": "tensorflow",
  }

  for file in headers:
    if file.endswith("cc.inc"):
      continue

    if any(i in file for i in path_to_exclude):
      continue

    for path, val in path_to_replace.items():
      if path in file:
        copy_file(file, os.path.join(srcs_dir, val), path)
        break
    else:
      copy_file(file, srcs_dir)

  create_local_config_python(os.path.join(srcs_dir,
                                          "external/local_config_python"))

  shutil.copytree(os.path.join(srcs_dir, "external/local_config_cuda/cuda"),
                  os.path.join(srcs_dir, "third_party/gpus"))
  shutil.copytree(os.path.join(srcs_dir, "tensorflow/compiler/xla"),
                  os.path.join(srcs_dir, "xla"))
  shutil.copytree(os.path.join(srcs_dir, "tensorflow/tsl"),
                  os.path.join(srcs_dir, "tsl"))


def prepare_srcs(deps: list[str], srcs_dir: str) -> None:
  """Rearrange source files in the directory."""
  path_to_replace = {
      "external/local_xla/": "tensorflow/compiler",
      "external/local_tsl/": "tensorflow",
  }

  for file in deps:
    for path, val in path_to_replace.items():
      if path in file:
        copy_file(file, os.path.join(srcs_dir, val), path)
        break
    else:
      # exclude external py files
      if "external" not in file:
        copy_file(file, srcs_dir)


def prepare_aot(aot: list[str], srcs_dir: str) -> None:
  for file in aot:
    if "external/local_tsl/" in file:
      copy_file(file, srcs_dir, "external/local_tsl/")
    elif "external/local_xla/" in file:
      copy_file(file, srcs_dir, "external/local_xla/")
    else:
      copy_file(file, srcs_dir)

  shutil.move(
      os.path.join(srcs_dir, ("tensorflow/tools/pip_package/v2/"
                              "xla_build/CMakeLists.txt")),
      os.path.join(srcs_dir, "CMakeLists.txt"),
  )


def prepare_wheel_srcs(
    headers: list[str], srcs: list[str], aot: list[str], srcs_dir: str,
    version: str) -> None:
  """Rearrange source and header files."""
  prepare_headers(headers, os.path.join(srcs_dir, "tensorflow/include"))
  prepare_srcs(srcs, srcs_dir)
  prepare_aot(aot, os.path.join(srcs_dir, "tensorflow/xla_aot_runtime_src"))

  # Every directory that contains a .py file gets an empty __init__.py file.
  create_init_files(os.path.join(srcs_dir, "tensorflow"))

  # move MANIFEST and THIRD_PARTY_NOTICES to the root
  shutil.move(
      os.path.join(srcs_dir, "tensorflow/tools/pip_package/v2/MANIFEST.in"),
      os.path.join(srcs_dir, "MANIFEST.in")
  )
  shutil.move(
      os.path.join(srcs_dir,
                   "tensorflow/tools/pip_package/v2/THIRD_PARTY_NOTICES.txt"),
      os.path.join(srcs_dir, "tensorflow/THIRD_PARTY_NOTICES.txt"),
  )

  update_xla_tsl_imports(os.path.join(srcs_dir, "tensorflow"))
  if not is_windows():
    rename_libtensorflow(os.path.join(srcs_dir, "tensorflow"), version)
  if not is_macos() and not is_windows():
    patch_so(srcs_dir)


def update_xla_tsl_imports(srcs_dir: str) -> None:
  """Workaround for TSL and XLA vendoring."""
  replace_inplace(srcs_dir, "from tsl", "from tensorflow.tsl")
  replace_inplace(
      srcs_dir,
      "from local_xla.xla",
      "from tensorflow.compiler.xla",
      )
  replace_inplace(
      srcs_dir, "from xla", "from tensorflow.compiler.xla"
  )


def patch_so(srcs_dir: str) -> None:
  """Patch .so files."""
  to_patch = {
      "tensorflow/python/_pywrap_tensorflow_internal.so":
      "$ORIGIN/../../tensorflow/tsl/python/lib/core",
      ("tensorflow/compiler/mlir/quantization/tensorflow/python/"
       "pywrap_function_lib.so"): "$ORIGIN/../../../../../python",
      ("tensorflow/compiler/mlir/quantization/tensorflow/python/"
       "pywrap_quantize_model.so"): "$ORIGIN/../../../../../python",
      ("tensorflow/compiler/mlir/quantization/tensorflow/calibrator/"
       "pywrap_calibration.so"): "$ORIGIN/../../../../../python",
  }
  for file, path in to_patch.items():
    subprocess.run(["patchelf", "--add-rpath", path,
                    "{}/{}".format(srcs_dir, file)], check=True)
    subprocess.run(["patchelf", "--shrink-rpath",
                    "{}/{}".format(srcs_dir, file)], check=True)


def rename_libtensorflow(srcs_dir: str, version: str):
  """Update version to major for libtensorflow_cc."""
  major_version = version.split(".")[0]
  if is_macos():
    shutil.move(
        os.path.join(srcs_dir, "libtensorflow_cc.{}.dylib".format(version)),
        os.path.join(
            srcs_dir, "libtensorflow_cc.{}.dylib".format(major_version)
        ),
    )
    shutil.move(
        os.path.join(
            srcs_dir, "libtensorflow_framework.{}.dylib".format(version)
        ),
        os.path.join(
            srcs_dir, "libtensorflow_framework.{}.dylib".format(major_version)
        ),
    )
  else:
    shutil.move(
        os.path.join(srcs_dir, "libtensorflow_cc.so.{}".format(version)),
        os.path.join(srcs_dir, "libtensorflow_cc.so.{}".format(major_version)),
    )
    shutil.move(
        os.path.join(srcs_dir, "libtensorflow_framework.so.{}".format(version)),
        os.path.join(
            srcs_dir, "libtensorflow_framework.so.{}".format(major_version)
        ),
    )


def create_local_config_python(dst_dir: str) -> None:
  """Copy python and numpy header files to the destination directory."""
  shutil.copytree(
      "external/pypi_numpy/site-packages/numpy/core/include",
      os.path.join(dst_dir, "numpy_include"),
  )
  if is_windows():
    path = "external/python_*/include"
  else:
    path = "external/python_*/include/python*"
  shutil.copytree(glob.glob(path)[0], os.path.join(dst_dir, "python_include"))


def build_wheel(dir_path: str, cwd: str, project_name: str) -> None:
  env = os.environ.copy()
  if is_windows():
    env["HOMEPATH"] = "C:"
  env["project_name"] = project_name

  subprocess.run(
      [sys.executable, "tensorflow/tools/pip_package/v2/setup.py",
       "bdist_wheel",
       f"--dist-dir={dir_path}"], check=True, cwd=cwd, env=env)


if __name__ == "__main__":
  args = parse_args()

  temp_dir = tempfile.TemporaryDirectory(prefix="tensorflow_wheel")
  temp_dir_path = temp_dir.name
  try:
    prepare_wheel_srcs(args.headers, args.srcs, args.xla_aot,
                       temp_dir_path, args.version)
    build_wheel(os.path.dirname(os.path.join(os.getcwd(), args.output_name)),
                temp_dir_path, args.project_name)
  finally:
    temp_dir.cleanup()
