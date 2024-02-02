# Copyright 2022 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
# pylint: disable=g-import-not-at-top
"""Script to start GRPC worker as a service.

Usage:
    python3 grpc_tpu_worker_service.py
"""

import os
import subprocess
import sys

SERVICE_FILE_CONTENT = f"""
[Unit]
Description=GRPC TPU Worker Service
After=network.target

[Service]
Type=simple
Environment="HOME=/home/tpu-runtime"
EnvironmentFile=/home/tpu-runtime/tpu-env
ExecStartPre=/bin/mkdir -p /tmp/tflogs
ExecStartPre=/bin/touch /tmp/tflogs/grpc_tpu_worker.log
ExecStartPre=/bin/chmod +r /tmp/tflogs
ExecStart=start_grpc_tpu_worker 2>&1 | tee -a /tmp/tflogs/grpc_tpu_worker.log
Restart=on-failure
# Restart service after 10 seconds if the service crashes:
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
SERVICE_NAME = "grpc_tpu_worker.service"


def create_systemd_service_file(service_content, service_name):
  with open(service_name, "w") as file:
    file.write(service_content)
  print(f"Service file {service_name} created")


def move_file_to_systemd(service_name):
  command = f"sudo mv {service_name} /etc/systemd/system/{service_name}"
  subprocess.run(command, shell=True, check=True)
  print(f"Service file moved to /etc/systemd/system/{service_name}")


def enable_start_service(service_name):
  commands = [
      "sudo systemctl daemon-reload",
      f"sudo systemctl enable {service_name}",
      f"sudo systemctl start {service_name}",
  ]
  for command in commands:
    subprocess.run(command, shell=True, check=True)
    print(f"Executed: {command}")


def run():
  if os.path.exists(f"/etc/systemd/system/{SERVICE_NAME}"):
    print(f"Service file /etc/systemd/system/{SERVICE_NAME} already exists")
    sys.exit(1)
  else:
    create_systemd_service_file(SERVICE_FILE_CONTENT, SERVICE_NAME)
    move_file_to_systemd(SERVICE_NAME)
    enable_start_service(SERVICE_NAME)


if __name__ == '__main__':
  run()
