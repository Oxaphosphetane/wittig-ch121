import json
import enum
from typing import List, Dict
from collections import defaultdict


class JobInfo(enum.Enum):
    JOB_ID = 'job_id'
    JOB_STATUS = 'job_status'


class JobStatus(enum.Enum):
    PENDING = 'PENDING'
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"


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
            unique_molecules['ald_smiles'].add(entry['ald_smiles'])
            unique_molecules['ylide_smiles'].add(entry['ylide_smiles'])
            unique_molecules['cis_pdt'].add(entry['cis_pdt'])
            unique_molecules['trans_pdt'].add(entry['trans_pdt'])

        # Convert sets to lists
        for key in unique_molecules:
            unique_molecules[key] = list(unique_molecules[key])

        return unique_molecules

