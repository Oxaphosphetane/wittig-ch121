"""
For dealing with smiles vs canonical smiles
"""

from job import *
import molecule as mol
from typing import List
from job_utils import JsonParser
import subprocess
import math

from dft_parameters import DFTBases, DFTMethods
from job_manager import JobManager

from config import Config, ConfigKeys

config = Config()


def main():
    job_manager = JobManager(config.get_file(ConfigKeys.OUT_DIR))
    molecules = job_manager.build_molecule_list(data_path=config.get_file(ConfigKeys.MOLECULE_SOURCE))

    path_to_job_tracker = config.get_file(ConfigKeys.JOB_TRACKER)
    batched_jobs = pd.read_csv(path_to_job_tracker)

    for


if __name__ == "__main__":
    main()
