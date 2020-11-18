import toml
from modules import log

logger = log.get_logger(__name__)


class Config:
    def __init__(self, filename):
        self.json = toml.load(filename)
        self.validate_config()

    def quit_on_empty(self, value):
        if value is None or value == "":
            logger.error("Error parsing config file. One of the values is empty.")
            quit()
        else:
            return value

    def validate_config(self):
        try:
            self.owner_id = self.quit_on_empty(self.json["owner_id"])
            self.prefix = self.quit_on_empty(self.json["prefix"])
            self.discord_token = self.quit_on_empty(self.json["keys"]["discord_token"])
            self.dbcredentials = self.quit_on_empty(self.json["database"])
        except KeyError as e:
            logger.error("Error parsing config file. Something must be missing.")
            logger.error(e)
            quit()
