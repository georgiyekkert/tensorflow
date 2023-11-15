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
import os
import pathlib
import sys
import subprocess
import shutil
import tempfile

from typing import Sequence

def create_temp_dir():
  return tempfile.TemporaryDirectory(prefix="tensorflow_wheel")

def parse_args():
  parser = argparse.ArgumentParser(
      description='Helper for building pip packages', fromfile_prefix_chars='@')
  parser.add_argument(
      "--output-name",
      required=True,
      help="Output file for the wheel, mandatory"
  )
  parser.add_argument(
      "--headers",
      help="header files of the wheel",
      action='append'
  )
  parser.add_argument(
      "--srcs",
      help="header files of the wheel",
      action='append'
  )
  parser.add_argument(
      "--deps",
      help="header files of the wheel",
      action='append'
  )
  parser.add_argument(
      "--xla_aot",
      help="xla aot compiled sources",
      action='append'
  )
  return parser.parse_args()

headers_to_exclude = [
    "external/pypi",
    "local_config_cuda/cuda/_virtual_includes",
    "local_config_tensorrt",
    "python_x86_64",
    "python_aarch64",
    "llvm-project/llvm/",
]


def prepare_wheel(headers, deps, srcs, aot, srcs_dir):
  for file in headers:
    if any(i in file for i in headers_to_exclude):
      continue
    elif "bazel-out/k8-opt/bin/" in file:
      copy_file(file, srcs_dir+"/tensorflow/include", "bazel-out/k8-opt/bin/")
    elif "external/com_google_absl/" in file:
      copy_file(file, srcs_dir+"/tensorflow/include", "external/com_google_absl/")
    elif "external/eigen_archive/Eigen/" in file:
      copy_file(file, srcs_dir+"/tensorflow/include", "external/eigen_archive/")
    elif "external/eigen_archive/unsupported/" in file:
      copy_file(file, srcs_dir+"/tensorflow/include", "external/eigen_archive/")
    elif "external/jsoncpp_git/include/" in file:
      copy_file(file, srcs_dir+"/tensorflow/include/include", "external/jsoncpp_git/include/")
    elif "external/com_google_protobuf/src/" in file:
      copy_file(file, srcs_dir+"/tensorflow/include", "external/com_google_protobuf/src/")
    else:
      copy_file(file, srcs_dir+"/tensorflow/include", None)

  for file in deps:
    if "external/pypi" in file:
      continue
    elif "bazel-out/k8-opt/bin/external/local_xla/" in file:
      copy_file(file, srcs_dir+"/tensorflow/compiler/xla", "bazel-out/k8-opt/bin/external/local_xla/", create_init=True)
    elif "bazel-out/k8-opt/bin/external/local_tsl/" in file:
      copy_file(file, srcs_dir+"/tensorflow/tsl", "bazel-out/k8-opt/bin/external/local_tsl/", create_init=True)
    elif "bazel-out/k8-opt/bin/" in file:
      copy_file(file, srcs_dir, "bazel-out/k8-opt/bin/", create_init=True)
    else:
      copy_file(file, srcs_dir, None, create_init=True)

  for file in srcs:
    if "bazel-out/k8-opt/bin/" in file:
      copy_file(file, srcs_dir, "bazel-out/k8-opt/bin/")
    else:
      copy_file(file, srcs_dir, None)

  for file in aot:
    if "external/local_tsl/" in file:
      copy_file(file, srcs_dir+"/tensorflow/xla_aot_runtime_src", "external/local_tsl/")
    elif "external/local_xla/" in file:
      copy_file(file, srcs_dir+"/tensorflow/xla_aot_runtime_src", "external/local_xla/")
    else:
      copy_file(file, srcs_dir+"/tensorflow/xla_aot_runtime_src", None)

  shutil.move(srcs_dir+"/tensorflow/tools/pip_package/THIRD_PARTY_NOTICES.txt", srcs_dir+"/tensorflow/THIRD_PARTY_NOTICES.txt")
def is_windows() -> bool:
  return sys.platform.startswith("win32")

def copy_file(
    src_file: str,
    dst_dir: str,
    strip: str = None,
    create_init: bool = False,
) -> None:
  if strip:
    src_file_no_prefix = src_file.removeprefix(strip)
  else:
    src_file_no_prefix = src_file
  dstdir = os.path.join(dst_dir, os.path.dirname(src_file_no_prefix))
  os.makedirs(dstdir, exist_ok=True)
  if create_init:
    if not os.path.exists(dstdir+"/__init__.py"):
      open(dstdir+"/__init__.py", 'a').close()

  shutil.copy(src_file, dstdir)

def build_wheel(name, dir):
  #copy_file("tensorflow/tools/pip_package/MANIFEST.in", dir, "tensorflow/tools/pip_package/")
  shutil.move(dir+"/tensorflow/tools/pip_package/MANIFEST.in", dir+"/MANIFEST.in")
  copy_file("tensorflow/tools/pip_package/setup.py", dir, "tensorflow/tools/pip_package/")
  #s = os.listdir(dir)
  #with open("tensorflow/tools/pip_package/test.txt", "w+") as file:
  #  file.write(",".join(s))

  subprocess.run(
      [sys.executable, "tensorflow/tools/pip_package/setup.py", "bdist_wheel",
       f"--dist-dir={name}"], check=True, cwd=dir)


if __name__ == "__main__":
  args = parse_args()
  headers = args.headers
  deps = args.deps
  srcs = args.srcs
  aot = args.xla_aot

  temp_dir = create_temp_dir()
  temp_dir_path = temp_dir.name
  try:
    os.makedirs(temp_dir_path+"/tensorflow/include", exist_ok=True)
    prepare_wheel(headers, deps, srcs, aot, temp_dir_path)
    build_wheel(os.getcwd()+"/"+args.output_name, temp_dir_path)
  finally:
    temp_dir.cleanup()
