import argparse
import asyncio
import socket
import urllib.parse
from typing import Tuple

import bittensor as bt


def build_url(ip_addr, port):
    parsed_ip = urllib.parse.urlparse(ip_addr)
    scheme = parsed_ip.scheme if parsed_ip.scheme else "http"
    netloc = parsed_ip.netloc if parsed_ip.netloc else ip_addr
    return f"{scheme}://{netloc}:{port}"


async def is_live(host: str, port: int = 80, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        await asyncio.wait_for(
            asyncio.get_event_loop().sock_connect(sock, (host, port)), timeout
        )
    except asyncio.TimeoutError:
        return False
    except Exception:
        return False
    else:
        sock.close()
        return True


def get_config():
    """Returns the configuration object specific to this miner or validator after adding relevant arguments."""
    parser = argparse.ArgumentParser()
    bt.subtensor.add_args(parser)
    bt.logging.add_args(parser)
    _config = bt.config(parser)
    bt.logging.check_config(_config)
    return _config


def initialise(
    config: bt.config,
) -> Tuple[bt.subtensor, bt.metagraph]:
    # These are core Bittensor classes to interact with the network.
    bt.logging.info("Setting up bittensor objects....")
    # The subtensor is our connection to the Bittensor blockchain.
    subtensor = bt.subtensor(config=config)
    bt.logging.info(f"Subtensor: {subtensor}")
    # The metagraph holds the state of the network, letting us know about other validators and miners.
    metagraph = subtensor.metagraph(config.netuid)
    bt.logging.info(f"Metagraph: {metagraph}")
    # The axon handles request processing, allowing validators to send this miner requests.
    return subtensor, metagraph


def is_miner(metagraph: bt.metagraph, uid: int) -> bool:
    """Check if uid is a validator. NOTE: this code is duplicated on subnet code side."""
    stakes = metagraph.S.tolist()
    return stakes[uid] < 1_000
