import json

import os
import os_navigation as os_nav
import enum


class ConfigKeys(enum.Enum):
    HPC_RESOURCES = 'hpc_resources'
    CORES = 'cores'
    MEMORY = 'memory'
    WALLTIME = 'walltime'

    JOBS = 'jobs'
    BATCH_SIZE = 'batch_size'
    SOFTWARE = 'software'
    JOB_SPECS = 'job_specs'
    JOB_TYPE = 'job_type'
    PROPERTIES = 'properties'
    VIB_FREQS = 'vib_freqs'
    DFT_SPECS = 'dft_specs'
    METHOD = 'method'
    BASIS = 'basis'

    FILES = 'files'
    MOLECULES = 'molecules'
    MOLECULE_SOURCE = 'molecule_source'
    OUT_DIR = "out_dir"
    JOB_TRACKER = 'job_tracker'


class Config:
    def __init__(self, _config_path=os.path.join(os_nav.find_project_root(), 'config.json')):
        with open(_config_path, 'r') as f:
            self.data = json.load(f)

    def get_hpc_resource(self, key: ConfigKeys):
        return self.data[ConfigKeys.HPC_RESOURCES.value][key.value]

    def get_job_spec(self, key: ConfigKeys):
        try:
            return self.data[ConfigKeys.JOBS.value][ConfigKeys.JOB_SPECS.value][key.value]
        except KeyError:
            return self.data[ConfigKeys.JOBS.value][key.value]

    def get_dft_spec(self, key: ConfigKeys):
        return self.data[ConfigKeys.JOBS.value][ConfigKeys.DFT_SPECS.value][key.value]

    def get_properties_to_calculate(self):
        properties_dict = self.data[ConfigKeys.JOBS.value][ConfigKeys.PROPERTIES.value]
        for prop in properties_dict:
            properties_dict[prop] = bool(properties_dict[prop])
        return properties_dict

    def get_file(self, key: ConfigKeys):
        file_ext = self.data[ConfigKeys.FILES.value][key.value]
        return os.path.normpath(os.path.join(os_nav.find_project_root(), file_ext))
