from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from sqlite3 import Cursor, Connection
import yaml
from db_handler import SqliteHandler


@dataclass
class MeadTracker(SqliteHandler):

    db_name: str = "mah_dope_meads.db"

    def __post_init__(self) -> None:
        """
        creates conn object
        """
        super().__init__(db_path=self.db_name)        
        self.cfg = yaml.safe_load(Path("cfg.yml").read_text())
        self.qrys = self.cfg["sql"]
        self.abv_fct = 131.25
        self.init_ddl = Path(self.cfg["init_ddl"]).read_text()
        # register custom functions
        self.db.conn.create_function("trg_starting_grav", 2, self.trg_starting_grav)
        # run initial ddl commands
        self.db.run_script(self.init_ddl)

    def ins_mead(self, mead_name, yeast_used, sugar_source):
        rqst = {
            "cmd": self.qrys["ins_new_mead"],
            "args": {
                "mead_name": mead_name,
                "yeast_used": yeast_used,
                "sugar_source": sugar_source,
            },
        }
        self.db.run_cmd(**rqst)
        # set the row_id of the last inserted row
        self.set_active_mead_id(self.db.crs.lastrowid)
        return

    def ins_abv_mead(self, mead_id):
        pass

    def set_active_mead_id(self, mead_id: int):
        """can be set from multiple places"""
        self.mead_id = mead_id

    def update_start_grav(self, mead_id, start_grav):
        rqst = {
            "cmd": self.qrys["updt_start_grav"],
            "args": {
                "mead_id": mead_id,
                "starting_gravity": start_grav,
                "potential_abv": self.pot_abv(start_grav),
            },
        }
        return self.db.run_cmd(**rqst)

    def get_mead_row(self, mead_id: int = None) -> namedtuple:
        m_id = self.mead_id if not mead_id else mead_id
        rqst = {
            "cmd": self.qrys["get_mead_row"],
            "args": {"mead_id": m_id},
        }
        rslt = self.db.run_cmd(**rqst).fetchone()
        return rslt

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
        mead_name="Boo; Blackberry Habanaero",
        sugar_source="Costco Wildflower Honey",
        yeast_used="K1-V1116",
    )
    mt.get_mead_row(mead_id=1)

# TODO:
# TODO: set up a trigger to insert 1) abv_measurement 2) activity records
# TODO: set up view to capture abv measurement
# starting_grav, curr_grab, curr_abv, pot_abv, etc, etc
