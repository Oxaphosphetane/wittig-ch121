from dft_parameters import *
from abc import ABC, abstractmethod

from job_utils import JobInfo, JobStatus, JobTypes


class Job(ABC):
    @abstractmethod
    def set_status(self, job_type: JobTypes, job_status: JobStatus):
        pass

    @abstractmethod
    def encode_id(self) -> str:
        pass

    @abstractmethod
    def is_new(self) -> bool:
        pass

    @abstractmethod
    def write_input(self) -> str:
        pass

    @abstractmethod
    def store(self):
        pass