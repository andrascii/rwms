# Copyright 2015 gRPC authors.
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
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function

import logging

import grpc
import asyncio
import vpn_manager_pb2
import vpn_manager_pb2_grpc

from datetime import datetime, timedelta, timezone
from google.protobuf.timestamp_pb2 import Timestamp

def to_proto_timestamp(dt: datetime) -> Timestamp:
  ts = Timestamp()
  ts.FromDatetime(dt)
  return ts

async def main():
  # NOTE(gRPC Python Team): .close() is possible on a channel and should be
  # used in circumstances in which the with statement does not fit the needs
  # of the code.
  logging.info("Will try to add user...")

  channel = grpc.aio.insecure_channel("localhost:50051")
  stub = vpn_manager_pb2_grpc.VpnManagerStub(channel)

  add_user_response = await stub.AddUser(
    vpn_manager_pb2.AddUserRequest(
      username="Administrator",
      email="apugachevdev@yandex.ru",
      telegram_id=594514115,
      expire_at=datetime.now(timezone.utc) + timedelta(days=7),
      activate_all_inbounds=True,
      status=vpn_manager_pb2.UserStatus.ACTIVE,
      traffic_limit_strategy=vpn_manager_pb2.TrafficLimitStrategy.NO_RESET
    )
  )

  logging.info(f"VpnManager client received:\n{add_user_response}")

  #if add_user_response.success == True:
  #  update_user_response = stub.UpdateUser(
  #     vpn_manager_pb2.UpdateUserRequest(
  #        
  #     )
  #  )

if __name__ == "__main__":
    logging.basicConfig(
      format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
      level=logging.INFO
    )
    
    logging.basicConfig()
    asyncio.run(main())
