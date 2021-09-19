import logging
import uvicorn
import pathlib


class logger_class:
    def __init__(self):
        self.logfile = "test.log"
        self.logger = logging.getLogger("uvicorn.access")
        self.setup_loging()

    def setup_loging(self):
        logger = logging.getLogger("uvicorn.access")
        console_formatter = uvicorn.logging.ColourizedFormatter(
            "{asctime} {levelprefix} : {message}",
            style="{", use_colors=True)
        logger.handlers[0].setFormatter(console_formatter)
        logfile = pathlib.Path(self.logfile)
        logfile.touch()
        logfile.chmod(0o666)
        handler = logging.FileHandler(filename=self.logfile)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)8s : %(message)s"))
        handler.setLevel(logging.WARN)
        logger.addHandler(handler)

        logger = logging.getLogger("uvicorn")
        console_formatter = uvicorn.logging.ColourizedFormatter(
            "{asctime} {levelprefix} : {message}",
            style="{", use_colors=True)
        logger.handlers[0].setFormatter(console_formatter)

    def error(self, message):
        self.logger.error(message)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)


logger = logger_class()
