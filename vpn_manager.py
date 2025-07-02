import os
import grpc
import logging

import vpn_manager_pb2
import vpn_manager_pb2_grpc

from typing import Optional
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp

from environments import (
    ENV_RW_BASE_URL,
    ENV_RW_TOKEN
)

from remnawave_api import RemnawaveSDK
from remnawave_api.models import UsersResponseDto, UserResponseDto

from remnawave_api.enums import ErrorCode, UserStatus, TrafficLimitStrategy
from remnawave_api.exceptions import ApiError
from remnawave_api.models import (
  CreateUserRequestDto,
  DeleteUserResponseDto,
  EmailUserResponseDto,
  TelegramUserResponseDto,
  UpdateUserRequestDto,
  UserResponseDto,
  UsersResponseDto,
  TagsResponseDto,
  RevokeUserRequestDto
)

def from_proto_timestamp(ts: Timestamp) -> datetime:
  return ts.ToDatetime()

def to_ts(dt: Optional[datetime]) -> Optional[Timestamp]:
  if dt is None:
    return None

  dt = dt.replace(tzinfo=timezone.utc)
  ts = Timestamp()
  ts.FromDatetime(dt)
  return ts

def RemnawaveUserStatusToProto(status: UserStatus) -> vpn_manager_pb2.UserStatus:
  """
  Converts a Remnawave UserStatus to a UserStatus protobuf enum.
  """
  if status == UserStatus.ACTIVE:
    return vpn_manager_pb2.UserStatus.ACTIVE
  elif status == UserStatus.DISABLED:
    return vpn_manager_pb2.UserStatus.DISABLED
  elif status == UserStatus.LIMITED:
    return vpn_manager_pb2.UserStatus.LIMITED
  elif status == UserStatus.EXPIRED:
    return vpn_manager_pb2.UserStatus.EXPIRED
  else:
    raise ValueError(f'Invalid user status: {status}')
  
def RemnawaveTrafficLimitStrategyToProto(strategy: TrafficLimitStrategy) -> vpn_manager_pb2.TrafficLimitStrategy:
  """
  Converts a Remnawave TrafficLimitStrategy to a TrafficLimitStrategy protobuf enum.
  """
  if strategy == TrafficLimitStrategy.NO_RESET:
    return vpn_manager_pb2.TrafficLimitStrategy.NO_RESET
  elif strategy == TrafficLimitStrategy.DAY:
    return vpn_manager_pb2.TrafficLimitStrategy.DAY
  elif strategy == TrafficLimitStrategy.WEEK:
    return vpn_manager_pb2.TrafficLimitStrategy.WEEK
  elif strategy == TrafficLimitStrategy.MONTH:
    return vpn_manager_pb2.TrafficLimitStrategy.MONTH
  else:
    raise ValueError(f'Invalid traffic limit strategy: {strategy}')

def dto_to_proto_user(user: UserResponseDto) -> vpn_manager_pb2.UserResponse:
  """
  Converts a UserResponseDto to a UserResponse protobuf message.
  """

  return vpn_manager_pb2.UserResponse(
    uuid=str(user.uuid),
    subscription_uuid=str(user.subscription_uuid),
    short_uuid=user.short_uuid,
    username=user.username,
    status=RemnawaveUserStatusToProto(user.status) if user.status else None,
    used_traffic_bytes=user.used_traffic_bytes,
    lifetime_used_traffic_bytes=user.lifetime_used_traffic_bytes,
    traffic_limit_bytes=user.traffic_limit_bytes if user.traffic_limit_bytes is not None else None,
    traffic_limit_strategy=RemnawaveTrafficLimitStrategyToProto(user.traffic_limit_strategy) if user.traffic_limit_strategy else None,
    sub_last_user_agent=user.sub_last_user_agent if user.sub_last_user_agent else None,
    sub_last_opened_at=to_ts(user.sub_last_opened_at),
    expire_at=to_ts(user.expire_at),
    online_at=to_ts(user.online_at),
    sub_revoked_at=to_ts(user.sub_revoked_at),
    last_traffic_reset_at=to_ts(user.last_traffic_reset_at),
    trojan_password=user.trojan_password,
    vless_uuid=str(user.vless_uuid),
    ss_password=user.ss_password,
    description=user.description if user.description else None,
    telegram_id=user.telegram_id if user.telegram_id else None,
    email=user.email if user.email else None,
    hwid_device_limit=user.hwidDeviceLimit if user.hwidDeviceLimit is not None else None,
    active_user_inbounds=[
      vpn_manager_pb2.UserActiveInbound(
        uuid=str(inb.uuid),
        tag=inb.tag,
        type=inb.type,
        network=inb.network if inb.network else None,
        security=inb.security if inb.security else None,
      )
      for inb in user.active_user_inbounds
    ],
    subscription_url=user.subscription_url,
    first_connected=to_ts(user.first_connected),
    last_trigger_threshold=user.last_trigger_threshold if user.last_trigger_threshold else None,
    last_connected_node=vpn_manager_pb2.UserLastConnectedNode(
      connected_at=to_ts(user.last_connected_node.connected_at),
      node_name=user.last_connected_node.node_name,
    ) if user.last_connected_node else None,
    happ=vpn_manager_pb2.HappCrypto(
      crypto_link=user.happ.cryptoLink,
    ) if user.happ else None,
    created_at=to_ts(user.created_at),
    updated_at=to_ts(user.updated_at),
  )

class VpnManager(vpn_manager_pb2_grpc.VpnManager):
  def __init__(self):
    super().__init__()
    rw_base_url = os.getenv(ENV_RW_BASE_URL)
    rw_token = os.getenv(ENV_RW_TOKEN)

    if not rw_base_url:
      raise ValueError(f"{ENV_RW_BASE_URL} environment variable is not set")
    
    if not rw_token:
      raise ValueError(f"{ENV_RW_TOKEN} environment variable is not set")

    print('Remnawave base url:', rw_base_url)
    print('Remnawave token:', rw_token)

    self.remnawave = RemnawaveSDK(
      base_url=rw_base_url,
      token=rw_token
    )

  async def AddUser(
      self,
      request: vpn_manager_pb2.AddUserRequest,
      context: grpc.aio.ServicerContext
  ) -> vpn_manager_pb2.AddUserReply:
    try:
      logging.info(f'Add user {request.username}')

      if request.status == vpn_manager_pb2.UserStatus.ACTIVE:
        status = UserStatus.ACTIVE
      elif request.status == vpn_manager_pb2.UserStatus.DISABLED:
        status = UserStatus.DISABLED
      elif request.status == vpn_manager_pb2.UserStatus.LIMITED:
        status = UserStatus.LIMITED
      elif request.status == vpn_manager_pb2.UserStatus.EXPIRED:
        status = UserStatus.EXPIRED
      else:
        logging.error(f'Invalid user status: {request.status}')
        return vpn_manager_pb2.AddUserReply(
          success=False,
          description=f'Invalid user status: {request.status}'
        )
      
      if request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.NO_RESET:
        traffic_limit_strategy = TrafficLimitStrategy.NO_RESET
      elif request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.DAY:
        traffic_limit_strategy = TrafficLimitStrategy.DAY
      elif request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.WEEK:
        traffic_limit_strategy = TrafficLimitStrategy.WEEK
      elif request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.MONTH:
        traffic_limit_strategy = TrafficLimitStrategy.MONTH
      else:
        logging.error(f'Invalid traffic limit strategy: {request.traffic_limit_strategy}')
        return vpn_manager_pb2.AddUserReply(
          success=False,
          description=f'Invalid traffic limit strategy: {request.traffic_limit_strategy}'
        )
      
      active_user_inbounds = list(request.active_user_inbounds)

      logging.info(f'received request {request}')

      created_user = await self.remnawave.users.create_user(
        CreateUserRequestDto(
          username=request.username,
          email=request.email,
          telegram_id=request.telegram_id,
          expire_at=from_proto_timestamp(request.expire_at),
          created_at=from_proto_timestamp(request.created_at) if request.created_at else None,
          activate_all_inbounds=request.activate_all_inbounds,
          status=status,
          traffic_limit_strategy=traffic_limit_strategy,
          active_user_inbounds=active_user_inbounds,
          description=request.description,
          tag=request.tag if request.tag else None,
          hwidDeviceLimit=request.hwid_device_limit,
          last_traffic_reset_at=from_proto_timestamp(request.last_traffic_reset_at) if request.last_traffic_reset_at else None,
        )
      )

      logging.info(f'User created: {created_user}')
      return vpn_manager_pb2.AddUserReply(success=True, response=dto_to_proto_user(created_user))
    except ApiError as e:
      logging.error(f'Add user operation failed: {e}')
      return vpn_manager_pb2.AddUserReply(
        success=False,
        error_info = vpn_manager_pb2.ErrorInfo(
          error_code=str(e.error.code),
          status_code=e.status_code,
          description=e.error.message
        )
      )
  
  async def UpdateUser(
      self,
      request: vpn_manager_pb2.UpdateUserRequest,
      context: grpc.aio.ServicerContext
  ) -> vpn_manager_pb2.UpdateUserReply:
    try:
      logging.info(f'Update user {request.uuid}')

      if request.status == vpn_manager_pb2.UserStatus.ACTIVE:
        status = UserStatus.ACTIVE
      elif request.status == vpn_manager_pb2.UserStatus.DISABLED:
        status = UserStatus.DISABLED
      elif request.status == vpn_manager_pb2.UserStatus.LIMITED:
        status = UserStatus.LIMITED
      elif request.status == vpn_manager_pb2.UserStatus.EXPIRED:
        status = UserStatus.EXPIRED
      else:
        logging.error(f'Invalid user status: {request.status}')
        return vpn_manager_pb2.AddUserReply(
          success=False,
          description=f'Invalid user status: {request.status}'
        )
      
      if request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.NO_RESET:
        traffic_limit_strategy = TrafficLimitStrategy.NO_RESET
      elif request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.DAY:
        traffic_limit_strategy = TrafficLimitStrategy.DAY
      elif request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.WEEK:
        traffic_limit_strategy = TrafficLimitStrategy.WEEK
      elif request.traffic_limit_strategy == vpn_manager_pb2.TrafficLimitStrategy.MONTH:
        traffic_limit_strategy = TrafficLimitStrategy.MONTH
      else:
        logging.error(f'Invalid traffic limit strategy: {request.traffic_limit_strategy}')
        return vpn_manager_pb2.AddUserReply(
          success=False,
          description=f'Invalid traffic limit strategy: {request.traffic_limit_strategy}'
        )
      
      active_user_inbounds = list(request.active_user_inbounds)

      updated_user = await self.remnawave.users.update_user(
        UpdateUserRequestDto(
          uuid=request.uuid,
          status=status,
          traffic_limit_bytes=request.traffic_limit_bytes,
          traffic_limit_strategy=traffic_limit_strategy,
          active_user_inbounds=active_user_inbounds,
          expire_at=from_proto_timestamp(request.expire_at),
          last_traffic_reset_at=from_proto_timestamp(request.last_traffic_reset_at) if request.last_traffic_reset_at else None,
          description=request.description,
          tag=request.tag,
          telegram_id=request.telegram_id,
          email=request.email,
          hwid_device_limit=request.hwid_device_limit
        )
      )

      logging.info(f'User updated: {updated_user}')
      return vpn_manager_pb2.UpdateUserReply(
        success=True,
        response=dto_to_proto_user(updated_user)
      )
    except ApiError as e:
      logging.error(f'Update user operation failed: {e}')
      return vpn_manager_pb2.AddUserReply(
        success=False,
        error_info = vpn_manager_pb2.ErrorInfo(
          error_code=str(e.error.code),
          status_code=e.status_code,
          description=e.error.message
        )
      )
    