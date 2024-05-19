from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from sqlite3 import Cursor, Connection
import yaml
from sqlite_handler import SqliteHandler


@dataclass
class TgtMead:
    db: Connection


@dataclass
class MeadTracker(SqliteHandler):
    db_name: str = "mah_dope_meads.db"
    abv_fct: float = 131.25
    mead_id: int = None
    verbose: bool = True

    def __post_init__(self, *args, **krags) -> None:
        """
        creates conn object
        """
        super().__init__(db_path=self.db_name, verbose=self.verbose, *args, **krags)
        self.cfg = yaml.safe_load(Path("cfg.yml").read_text())
        self.qrys = self.cfg["sql"]
        self.init_ddl = self.cfg["init_ddl"]
        # register custom functions
        self.conn.create_function("trg_starting_grav", 2, self.trg_starting_grav)
        # run initial ddl commands
        self.run_script_file(self.init_ddl)

    def ins_mead(
        self,
        mead_name: str,
        yeast_used: str,
        sugar_source: str,
        starting_gravity: float = None,
        potential_abv: float = None,
    ):
        rqst = {
            "cmd": self.qrys["ins_new_mead"],
            "args": {
                "mead_name": mead_name,
                "yeast_used": yeast_used,
                "sugar_source": sugar_source,
                "starting_gravity": starting_gravity,
                "potential_abv": potential_abv,
            },
        }
        # update if any others fields were passed in
        self.run_cmd(**rqst)
        # set the row_id of the last inserted row
        self.set_active_mead_id(self.crs.lastrowid)
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
        return self.run_fetchall(**rqst)

    def get_mead_row(self, mead_id: int = None) -> namedtuple:
        m_id = self.mead_id if not mead_id else mead_id
        rqst = {
            "cmd": self.qrys["get_mead_row"],
            "args": {"mead_id": m_id},
        }
        rslt = self.run_cmd(**rqst).fetchone()
        return rslt

    def trg_starting_grav(self, mead_id: int, str_grv: float) -> Cursor:
        """
        - updates the potential gravity in the meads table for mead_id
        - adds record to abv_measurement table
        - adds record to activity table
        """
        print(f"new starting grav for {mead_id=}: {str_grv=}")
        # update potential gravity
        r = self.run_cmd(
            cmd=self.qrys["update_pot_abv"],
            args={"potential_abv": self.pot_abv(str_grv), "mead_id": mead_id},
        )

    def pot_abv(self, start_grv):
        return (start_grv - 1) * self.abv_fct

    def curr_abv(self, mead_id, curr_grv):
        str_grv = self.get_mead_row(mead_id).starting_gravity
        return (str_grv - curr_grv) * self.abv_fct


def main():
    mt = MeadTracker(verbose=False)
    r = mt.ins_mead(
        mead_name="1Blackberry Habanaero",
        yeast_used="K1-V1116",
        sugar_source="Costco Wildflower Honey",
        starting_gravity=1.13,
    )
    print("boo")
    print(mt.get_mead_row(mead_id=1))

    # TODO:
    # TODO: set up view to capture abv measurement
    # starting_grav, curr_grab, curr_abv, pot_abv, etc, etc
    # TODO: add proper loggin


if __name__ == "__main__":
    main()
