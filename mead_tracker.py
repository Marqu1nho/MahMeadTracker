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
        self.conn: Connection = sqlite3.connect(f"./{self.db_name}")
        self.crs: Cursor = self.conn.cursor()
        self.init_ddl = Path(self.cfg["init_ddl"]).read_text()
        self.run_init_cmds()
        # register custom functions
        self.conn.create_function("fn_starting_gravity")
        pass

    def run_script(self, script) -> Cursor:
        with self.conn:
            return self.conn.executescript(script)

    def geg_single_val(self, cmd: str, fld_name: str) -> Cursor:
        pass

    def run_cmd(self, cmd: str, args: dict = None) -> Cursor:
        """
        run and commits a command
        """
        with self.conn:
            return self.conn.execute(cmd, args)

    def run_cfg_qry(self, qry_nm: str, args: dict = None) -> Cursor:
        """ """
        sql = self.cfg["sql"].get("qry_nm")
        return self.run_cmd(sql, args)

    def run_init_cmds(self) -> None:
        """
        runs all ddl commands at startup
        because they all have `if not exists` we're golden 🤩
        """
        self.run_script(self.init_ddl)

    def udf_starting_gravity_trigger(mead_id: int, str_grv: float) -> Cursor:
        """
        updates the activity table and abv_measurement table
        """
        qrys = {
            "ins_activity": {
                "mead_id": mead_id,
            },
            "ins_abv_meas": {
                "mead_id": mead_id,
                "curr_grv": str_grv,
            },
        }


if __name__ == "__main__":
    mt = MeadTracker()
