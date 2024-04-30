from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from sqlite3 import Cursor, Connection
import yaml


@dataclass
class MeadTracker:

    db_name: str = "mah_dope_meads.db"

    def __post_init__(self) -> None:
        """
        creates conn object
        """
        self.cfg = yaml.safe_load(Path("cfg.yml").read_text())
        self.qrys = self.cfg["sql"]
        self.abv_fct = 131.25
        self.conn: Connection = sqlite3.connect(f"./{self.db_name}")
        self.crs: Cursor = self.conn.cursor()
        self.init_ddl = Path(self.cfg["init_ddl"]).read_text()
        # register custom row factory
        self.conn.row_factory = self.nt_factory
        # register custom functions
        self.conn.create_function("trg_starting_grav", 2, self.trg_starting_grav)
        # create initial ddl
        self.run_init_cmds()
        pass

    def nt_factory(crs, row):
        hdrs = [h[0] for h in crs.description]
        return namedtuple("SQLite3Row", hdrs)(*row)

    def run_script(self, script) -> Cursor:
        with self.conn:
            return self.conn.executescript(script)

    def run_init_cmds(self) -> None:
        """
        runs all ddl commands at startup
        because they all have `if not exists` we're golden 🤩
        """
        self.run_script(self.init_ddl)

    def run_cmd(self, cmd: str, args: dict = None) -> Cursor:
        """
        run and commits a command
        """
        with self.conn:
            return self.conn.execute(cmd, args)

    def ins_mead(self, mead_name, yeast_used, sugar_source):
        qry = self.qrys["ins_new_mead"]
        args = {
            "mead_name": mead_name,
            "yeast_used": yeast_used,
            "sugar_source": sugar_source,
        }
        return self.run_cmd(qry, args)

    def update_start_grav(self, mead_id, start_grav):
        qry = self.qrys["updt_start_grav"]
        args = {
            "mead_id": mead_id,
            "starting_gravity": start_grav,
            "potential_abv": self.pot_abv(start_grav),
        }
        return self.run_cmd(qry, args)

    def get_mead_row(self, mead_id) -> namedtuple:
        qry, args = self.qrys["get_mead_row"], {"mead_id", mead_id}
        return self.run_cmd(qry, args).fetchone()[0]

    def trg_starting_grav(mead_id: int, str_grv: float) -> Cursor:
        """
        updates the activity table and abv_measurement table
        """
        # insert abv_measurement

    def pot_abv(self, start_grv):
        return (start_grv - 1) * self.abv_fct

    def curr_abv(self, mead_id, curr_grv):
        str_grv = self.get_mead_row(mead_id).starting_gravity
        return (str_grv - curr_grv) * self.abv_fct


if __name__ == "__main__":
    mt = MeadTracker()
    r = mt.ins_mead(
        mead_name="Pear Blackberry Habanaero",
        sugar_source="Costco Wildflower Honey",
        yeast_used="K1-V1116",
    )


# TODO: set up a trigger to insert 1) abv_measurement 2) activity records
# TODO: set up view to capture abv measurement
# starting_grav, curr_grab, curr_abv, pot_abv, etc, etc
