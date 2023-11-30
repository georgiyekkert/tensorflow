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

import argparse
import glob
import os
import sys
import subprocess
import shutil
import tempfile


def parse_args():
  parser = argparse.ArgumentParser(
      description='Helper for building pip packages', fromfile_prefix_chars='@')
  parser.add_argument(
      "--output-name", required=True,
      help="Output file for the wheel, mandatory")
  parser.add_argument("--project-name", required=True, help="Name")
  parser.add_argument(
      "--headers", help="header files for the wheel", action='append')
  parser.add_argument("--srcs", help="souirce files for the wheel",
                      action='append')
  parser.add_argument("--xla_aot", help="xla aot compiled sources",
                      action='append')
  return parser.parse_args()


def prepare_headers(headers, srcs_dir):
  """
  Rearrange header files in the source directory
  :param headers:
  :param srcs_dir:
  :return:
  """
  headers_to_exclude = [
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
      "external/local_xla/": "/tensorflow/compiler",
      "external/local_tsl/": "/tensorflow",
  }

  for file in headers:
    if file.endswith("cc.inc"):
      continue

    if any(i in file for i in headers_to_exclude):
      continue

    for path, val in path_to_replace.items():
      if path in file:
        copy_file(file, srcs_dir + val, path)
        break
    else:
      copy_file(file, srcs_dir)
  create_local_config_python(srcs_dir+"external/local_config_python/")

def prepare_srcs(deps, srcs_dir):
  path_to_replace = {
      "external/local_xla/": "/tensorflow/compiler",
      "external/local_tsl/": "/tensorflow",
  }

  for file in deps:
    for path, val in path_to_replace.items():
      if path in file:
        copy_file(file, srcs_dir + val, path)
        break
    else:
      if "external" not in file:
        copy_file(file, srcs_dir)

def prepare_aot(aot, srcs_dir):
  for file in aot:
    if "external/local_tsl/" in file:
      copy_file(file, srcs_dir,
                "external/local_tsl/")
    elif "external/local_xla/" in file:
      copy_file(file, srcs_dir,
                "external/local_xla/")
    else:
      copy_file(file, srcs_dir)

def prepare_wheel_srcs(headers, srcs, aot, srcs_dir):
  prepare_headers(headers, srcs_dir + "/tensorflow/include/")
  prepare_srcs(srcs, srcs_dir)
  prepare_aot(aot, srcs_dir+"/tensorflow/xla_aot_runtime_src")
  create_init_files(srcs_dir+"/tensorflow")
  shutil.move(
      srcs_dir + "/tensorflow/tools/pip_package/THIRD_PARTY_NOTICES.txt",
      srcs_dir + "/tensorflow/THIRD_PARTY_NOTICES.txt")

def is_windows() -> bool:
  return sys.platform.startswith("win32")

def create_local_config_python(dst_dir):
  shutil.copytree("external/pypi_numpy/site-packages/numpy/core/include", dst_dir+"/numpy_include")
  if is_windows():
    path = "python_*/include"
  else:
    path = "external/python_*/include/python*"
  shutil.copytree(glob.glob(path)[0], dst_dir+"/python_include")


def create_init_files(dst_dir):
  for root, dirs, files in os.walk(dst_dir):
    if any(file.endswith(".py") or file.endswith(".so") for file in files):
      curr_dir = root
      while curr_dir != dst_dir:
        init_path = os.path.join(curr_dir, "__init__.py")
        if not os.path.exists(init_path):
          open(init_path, "w").close()

        curr_dir = os.path.dirname(curr_dir)


def copy_file(
    src_file: str,
    dst_dir: str,
    strip: str = None,
) -> None:
  if src_file.startswith("bazel-out"):
    dest = src_file[src_file.index("bin")+4:]
  else:
    dest = src_file

  if strip:
    dest = dest.removeprefix(strip)
  dstdir = os.path.join(dst_dir, os.path.dirname(dest))
  os.makedirs(dstdir, exist_ok=True)
  shutil.copy(src_file, dstdir)


def build_wheel(name, dir, project_name):
  shutil.move(dir + "/tensorflow/tools/pip_package/MANIFEST.in",
              dir + "/MANIFEST.in")
  copy_file("tensorflow/tools/pip_package/setup.py", dir,
            "tensorflow/tools/pip_package/")

  subprocess.run(
      [sys.executable, "tensorflow/tools/pip_package/setup.py", "bdist_wheel",
       f"--dist-dir={name}"], check=True, cwd=dir)


if __name__ == "__main__":
  args = parse_args()

  temp_dir = tempfile.TemporaryDirectory(prefix="tensorflow_wheel")
  temp_dir_path = temp_dir.name
  try:
    prepare_wheel_srcs(args.headers, args.srcs, args.xla_aot,
                       temp_dir_path)
    build_wheel(os.path.dirname(os.getcwd() + "/" + args.output_name),
                temp_dir_path, args.project_name)
  finally:
    temp_dir.cleanup()
