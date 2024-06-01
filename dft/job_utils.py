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


class _JobType:
    def __init__(self, code: int, job_type: str, jaguar_class_name: str):
        self.code = code
        self.job_type = job_type
        self.jaguar_class_name = jaguar_class_name


class JobTypes(enum.Enum):
    UNSPECIFIED = _JobType(code=0, job_type='UNSPECIFIED', jaguar_class_name='JaguarJob')
    OPT = _JobType(code=1, job_type='OPT', jaguar_class_name='JaguarOptimization')
    TS_OPT = _JobType(code=2, job_type='TS_OPT', jaguar_class_name='JaguarTSOptimization')
    RC_SCAN = _JobType(code=3, job_type='RC_SCAN', jaguar_class_name='JaguarRCScan')

    @classmethod
    def from_code(cls, code: int):
        for e in cls:
            if e.value.code == code:
                return e
        return None

    @classmethod
    def from_name(cls, name: str):
        for e in cls:
            if e.value.job_type.lower() == name.lower():
                return e
        return None

