from collections import namedtuple
from dataclasses import dataclass
import sqlite3
from sqlite3 import Cursor, Connection


@dataclass
class DBHandler:
    db_name: str
    use_named_tuple_factory: bool = True

    def __post_init__(self) -> None:
        self.conn: Connection = sqlite3.connect(f"./{self.db_name}")
        self.crs: Cursor = self.conn.cursor()
        if self.use_named_tuple_factory:
            self.conn.row_factory = self.nt_factory

    @staticmethod
    def nt_factory(crs, row):
        hdrs = [h[0] for h in crs.description]
        return namedtuple("SQLite3Row", hdrs)(*row)

    def run_cmd(self, cmd: str, args: dict):
        with self.conn:
            return self.crs.execute(cmd, args)

    def run_script(self, script) -> Cursor:
        with self.conn:
            return self.crs.executescript(script)
