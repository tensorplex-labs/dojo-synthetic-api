# import argparse
# import os

# import bittensor as bt


# def check_config(config: bt.config):
#     """Checks/validates the config namespace object."""
#     bt.logging.check_config(config)

#     full_path = os.path.expanduser(
#         "{}/{}/{}/netuid{}/{}".format(
#             config.logging.logging_dir,
#             config.wallet.name,
#             config.wallet.hotkey,
#             config.netuid,
#             config.neuron.name,
#         )
#     )
#     config.neuron.full_path = os.path.expanduser(full_path)
#     if not os.path.exists(config.neuron.full_path):
#         os.makedirs(config.neuron.full_path, exist_ok=True)


# def add_args(parser):
#     parser.add_argument("--netuid", type=int, help="Subnet netuid", default=98)


# def get_config():
#     """Returns the configuration object specific to this miner or validator after adding relevant arguments."""
#     parser = argparse.ArgumentParser()
#     bt.wallet.add_args(parser)
#     bt.subtensor.add_args(parser)
#     bt.logging.add_args(parser)
#     bt.axon.add_args(parser)
#     add_args(parser)
#     _config = bt.config(parser)

#     check_config(_config)
#     return _config
