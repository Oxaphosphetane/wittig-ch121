import json
import enum
from typing import List, Dict
from collections import defaultdict
from rdkit import Chem


class JobSoftware(enum.Enum):
    JAGUAR = 'J'
    XTB = 'X'
    ORCA = 'O'


class JobInfo(enum.Enum):
    JOB_ID = 'job_id'
    JOB_STATUS = 'job_status'
    RUNTIME = 'runtime'


class JobStatus(enum.Enum):
    PENDING = 'PENDING'
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"


class DataJsonColumns(enum.Enum):
    ALD_SMILES = 'ald_smiles'
    YLIDE_SMILES = 'ylide_smiles'
    CIS_PDT = 'cis_pdt'
    TRANS_PDT = 'trans_pdt'


class JsonParser:
    def __init__(self, json_file: str):
        self.json_file = json_file
        self.data = self._load_json()

    def _load_json(self) -> Dict:
        with open(self.json_file, 'r') as file:
            return json.load(file)

    def get_unique_molecules(self) -> Dict[str, List[str]]:
        unique_molecules = defaultdict(set)
        for entry in self.data:
            for col in DataJsonColumns:
                col_name = col.value
                try:
                    unique_molecules[col_name].add(Chem.CanonSmiles(entry[col_name]))
                except Exception as e:
                    continue

        # Convert sets to lists
        for key in unique_molecules:
            unique_molecules[key] = list(unique_molecules[key])

        return unique_molecules
