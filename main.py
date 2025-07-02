import json
import asyncio
import logging
import grpc
import vpn_manager_pb2_grpc

from vpn_manager import VpnManager

logger = logging.getLogger(__name__)

def parse_json(json_string, default=None):
  """
  Парсит JSON строку с обработкой ошибок.
  Возвращает default при ошибке (по умолчанию None).
  """
  try:
    return json.loads(json_string)
  except json.JSONDecodeError:
    return default
  except Exception:
    return default
  

async def main():
  listen_addr = '[::]:50051'

  server = grpc.aio.server()
  server.add_insecure_port(listen_addr)
  vpn_manager_pb2_grpc.add_VpnManagerServicer_to_server(VpnManager(), server)

  logging.info(f'Server will listen on {listen_addr}')

  await server.start()
  await server.wait_for_termination()


if __name__ == "__main__":
  logging.basicConfig(
    format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
    level=logging.INFO
  )
  
  logging.basicConfig(level=logging.INFO)
  asyncio.run(main())
