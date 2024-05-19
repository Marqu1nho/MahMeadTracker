# standard
from collections import namedtuple
from functools import cached_property
from pathlib import Path
import sqlite3
from sqlite3 import Cursor, Connection


class SqliteHandler:
    """
    simple class to simplify working with sqlite DBs
    """

    # full path for where db will be read from or written
    def __init__(
        self,
        db_path: str = ":memory:",
        verbose: bool = True,
        use_named_tuple_factory: bool = True,
        *args,
        **kwargs,
    ) -> None:
        # capture init args
        self.db_path = db_path
        self.use_named_tuple_factory = use_named_tuple_factory
        self.verbose = verbose
        # create connection and cursor objects
        self.conn: Connection = sqlite3.connect(self.db_path)
        # row factory has to be set before cursor is created
        if self.use_named_tuple_factory:
            self.conn.row_factory = self.nt_factory
            print("registered named tuple row factory")
        self.crs: Cursor = self.conn.cursor()

    @staticmethod
    def nt_factory(crs, row):
        """
        converts a list to named tuple
        """
        hdrs = [h[0] for h in crs.description]
        return namedtuple("SQLite3Row", hdrs)(*row)

    @cached_property
    def db_name(self) -> str:
        """
        returns the name of the db file
        """
        return Path(self.db_path).name

    def run_cmd(self, cmd: str, args=None) -> Cursor:
        """
        runs single commands
        auto commits
        """
        args = tuple() if not args else args
        if self.verbose:
            print(f"{cmd=}")
        with self.conn:
            return self.crs.execute(cmd, args)

    def run_fetchone(self, cmd: str, args=None) -> tuple:
        """
        uses run cmd but returns fetch one method
        """
        return self.run_cmd(cmd, args).fetchone()

    def run_fetchmany(self, cmd: str, size: int = 10, args=None) -> tuple:
        """
        uses run cmd but returns fetch many method
        """
        return self.run_cmd(cmd, args).fetchmany(size=size)

    def run_fetchall(self, cmd: str, args=None) -> tuple:
        """
        uses run cmd but returns fetch all method
        """
        return self.run_cmd(cmd, args).fetchall()

    def run_many(self, cmd: str, args=None) -> Cursor:
        """
        typically insert statements
        auto commits
        """
        args = tuple() if not args else args
        if self.verbose:
            print(f"{cmd=}")
        with self.conn:
            return self.crs.executemany(cmd, args)

    def run_script_str(self, script: str) -> Cursor:
        """
        can run a string containing multiple statements
        auto commits
        """
        if self.verbose:
            print(f"{script=}")
        with self.conn:
            return self.crs.executescript(script)

    def run_script_file(self, script_file: Path) -> Cursor:
        """
        can run a string containing multiple statements
        auto commits
        """
        if self.verbose:
            print(f"{script_file=}")
        fl: Path = script_file if isinstance(script_file, Path) else Path(script_file)
        self.run_script_str(script=fl.read_text())

    def close_db(self) -> None:
        """
        closes the db
        """
        self.conn.close()
        print(f"closed {self.db_name=} @ {self.db_path=}")
