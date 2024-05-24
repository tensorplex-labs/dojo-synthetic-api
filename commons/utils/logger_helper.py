import logging
import os

class LoggerHelper:
    def __init__(self, logger_name: str,logging_level: int = logging.DEBUG):
        self.logger = self._setUpLogger(logger_name, logging_level)
        

    def _setUpLogger(self, logger_name: str, logging_level: int) -> logging.Logger:

        # Create a logger with the current module's name
        logger = logging.getLogger(logger_name)

        # Set the logger's level to DEBUG
        logger.setLevel(logging_level)

        formatter = logging.Formatter(
            "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def get_logger(self) -> logging.Logger:
        return self.logger
