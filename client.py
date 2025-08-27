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
import rwmanager_pb2
import rwmanager_pb2_grpc

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

    channel = grpc.aio.insecure_channel("localhost:50052")
    stub = rwmanager_pb2_grpc.RwManagerStub(channel)
    result = await stub.GetAllUsers(rwmanager_pb2.GetAllUsersRequest(offset=0, count=10))
    logging.info(f"rwms client received: {result}")

    #add_user_response = await stub.AddUser(
    #   rwmanager_pb2.AddUserRequest(
    #       username="Administrator",
    #       email="apugachevdev@yandex.ru",
    #       telegram_id=594514115,
    #       expire_at=datetime.now(timezone.utc) + timedelta(days=7),
    #       activate_all_inbounds=True,
    #       status=rwmanager_pb2.UserStatus.ACTIVE,
    #       traffic_limit_strategy=rwmanager_pb2.TrafficLimitStrategy.NO_RESET,
    #   )
    #)

    #for i in range(100000):
    #    await stub.AddUser(
    #        rwmanager_pb2.AddUserRequest(
    #            username=str(200000 + i + 5675),
    #            email="apugachevdev@yandex.ru",
    #            telegram_id=594514115,
    #            expire_at=datetime.now(timezone.utc) + timedelta(days=7),
    #            activate_all_inbounds=True,
    #            status=rwmanager_pb2.UserStatus.ACTIVE,
    #            traffic_limit_strategy=rwmanager_pb2.TrafficLimitStrategy.NO_RESET,
    #        )
    #    )

    #response = await stub.GetUserByUsername(
    #    rwmanager_pb2.GetUserByUsernameRequest(username="Administrator")
    #)
    #logging.info(f"rwms client received:\n{response}")
#
    #if response:
    #    update_user_response = await stub.UpdateUser(
    #        rwmanager_pb2.UpdateUserRequest(
    #            uuid=response.uuid,
    #            email="new_email@example.com",
    #            telegram_id=123456789,
    #            expire_at=datetime.now(timezone.utc) + timedelta(days=30),
    #            status=rwmanager_pb2.UserStatus.ACTIVE,
    #            traffic_limit_strategy=rwmanager_pb2.TrafficLimitStrategy.NO_RESET,
    #        )
    #    )
#
    #    logging.info(f"rwms client received:\n{update_user_response}")


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", level=logging.INFO
    )

    logging.basicConfig()
    asyncio.run(main())
