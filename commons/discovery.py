import asyncio
import copy
from typing import List

import bittensor as bt

from commons.utils import build_url, get_config, initialise, is_live, is_miner


class DiscoveryService:
    """A service that constantly discovers the validator URLs for being able to
    send requests to the validators for external requests in the future."""

    # NOTE @dev i have left some type hints for you
    lock: asyncio.Lock
    metagraph: bt.metagraph
    subtensor: bt.subtensor
    validator_urls: List

    def __init__(self):
        self.lock = asyncio.Lock()
        self.subtensor, self.metagraph = initialise(config=get_config())
        self.resync_metagraph()
        self._validator_urls = []

    async def run(self):
        while True:
            if (is_changed := self.resync_metagraph()) and is_changed:
                await self.discover_validator_urls()

            await asyncio.sleep(2 * bt.__blocktime__)

    async def discover_validator_urls(self):
        """Goal here is to figure out a list of validator URLs where we can send requests to,
        since in our subnet code we have used FastAPI to expose validator endpoints."""

        # see dojo-subnet's config.py
        # TODO @dev if they change default port, can read wandb logs to discover api.port
        DEFAULT_PORT = 1888

        max_uid = self.metagraph.n.item()
        assert max_uid + 1 == len(self.metagraph.axons)

        validator_ips = [axon.ip for axon in self.metagraph.axons]
        for i in range(max_uid):
            if is_miner(self.metagraph, i):
                continue
            validator_axon: bt.AxonInfo = self.metagraph.axons[i]
            validator_ips.append(validator_axon.ip)

        # NOTE not sure if there is a max number of connections, untested atm.
        is_validator_axon_alive: List[bool] = await asyncio.gather(
            *[is_live(ip, DEFAULT_PORT) for ip in validator_ips]
        )

        live_validator_urls = [
            build_url(ip, DEFAULT_PORT)
            for ip, alive in zip(validator_ips, is_validator_axon_alive)
            if alive
        ]
        self._validator_urls = live_validator_urls

    def resync_metagraph(self):
        """Sync the metagraph. NOTE this function returns a bool so we can use that info"""

        # Copies state of metagraph before syncing.
        previous_metagraph = copy.deepcopy(self.metagraph)

        # Sync the metagraph.
        self.metagraph.sync(subtensor=self.subtensor)
        # create a copy to freeze it in time

        # Check if the metagraph axon info has changed.
        if previous_metagraph.axons == self.metagraph.axons:
            bt.logging.info("Metagraph unchanged")
            return False

        return True
