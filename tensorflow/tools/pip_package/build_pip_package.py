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
  return parser.parse_args()

headers_to_exclude = [
    "external/pypi",
    "local_config_cuda/cuda/_virtual_includes",
    "local_config_tensorrt",
    "python_x86_64",
    "python_aarch64",
    "llvm-project/llvm/",
    "local_tsl",
    "local_xla",
]


def prepare_wheel(headers, deps, srcs, srcs_dir):
  for file in headers:
    if any(i in file for i in headers_to_exclude):
      continue
    elif "bazel-out/k8-opt/bin/" in file:
      copy_file(file, srcs_dir+"/tensorflow/include", "bazel-out/k8-opt/bin/")
    else:
      copy_file(file, srcs_dir+"/tensorflow/include", None)

  for file in deps:
    if "external/pypi" in file:
      continue
    elif "bazel-out/k8-opt/bin/" in file:
      copy_file(file, srcs_dir, "bazel-out/k8-opt/bin/")
    else:
      copy_file(file, srcs_dir, None)

  for file in srcs:
    if "bazel-out/k8-opt/bin/" in file:
      copy_file(file, srcs_dir, "bazel-out/k8-opt/bin/")
    else:
      copy_file(file, srcs_dir, None)


def is_windows() -> bool:
  return sys.platform.startswith("win32")

def copy_file(
    src_file: str,
    dst_dir: str,
    strip: str = None,
) -> None:
  if strip:
    src_file_no_prefix = src_file.removeprefix(strip)
  else:
    src_file_no_prefix = src_file
  dstdir = os.path.join(dst_dir, os.path.dirname(src_file_no_prefix))
  os.makedirs(dstdir, exist_ok=True)
  shutil.copy(src_file, dstdir)

def build_wheel(name, dir):
  copy_file("tensorflow/tools/pip_package/MANIFEST.in", dir, "tensorflow/tools/pip_package/")
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

  temp_dir = create_temp_dir()
  temp_dir_path = temp_dir.name
  try:
    os.makedirs(temp_dir_path+"/tensorflow/include", exist_ok=True)
    prepare_wheel(headers, deps, srcs, temp_dir_path)
    build_wheel(os.getcwd()+"/"+args.output_name, temp_dir_path)
  finally:
    temp_dir.cleanup()
