from dft_parameters import *
import os
import os_navigation as os_nav
import enum
import pandas as pd

from rdkit import Chem
import molecule as mol

from collections import Counter

job_storage_path = os.path.join(os_nav.find_project_root(), 'data', 'jobs')
mol_storage_path = os.path.join(os_nav.find_project_root(), 'data', 'mols')


class JobInfo(enum.Enum):
    JOB_ID = 'job_id'
    JOB_STATUS = 'job_status'


class JobStatus(enum.Enum):
    PENDING = 'PENDING'
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"


class _JobType:
    def __init__(self, code: int, job_type: str):
        self.code = code
        self.job_type = job_type


class JobTypes(enum.Enum):
    UNSPECIFIED = _JobType(code=0, job_type='UNSPECIFIED')
    OPT = _JobType(code=1, job_type='OPT')
    TS_OPT = _JobType(code=2, job_type='TS_OPT')
    RC_SCAN = _JobType(code=3, job_type='RC_SCAN')

    @classmethod
    def from_code(cls, code: int):
        for method in cls:
            if method.value.code == code:
                return method
        return None


class Stereochem(enum.Enum):
    NO_STEREO = 'A'
    E = 0
    Z = 1
    R = 2
    S = 3


def retrieve_job(job_id: str, store_path: str):
    jobs = pd.read_csv(store_path)

    assert job_id in jobs[JobInfo.JOB_ID.value].values

    retrieved_job = jobs[jobs[JobInfo.JOB_ID.value] == job_id]
    job_tuple = tuple(retrieved_job.iloc[0])

    return job_tuple


def retrieve_mols(mol_ids: list[str], store_path: str) -> list[mol.Molecule]:
    mols = []
    for mol_id in mol_ids:
        if 's' in mol_id:
            mol_container = os.path.join(store_path, 'solvents.csv')
            idx, qty = mol_id.split('s')
        elif 'a' in mol_id:
            mol_container = os.path.join(store_path, 'additives.csv')
            idx, qty = mol_id.split('a')
        else:
            mol_container = os.path.join(store_path, 'wittig_reactants.csv')
            idx = mol_id
            qty = 1

        for i in range(int(qty)):
            container = pd.read_csv(mol_container, index_col=0)
            mol_smiles = container.loc[idx, 'reactant_smiles']
            mols.append(mol.Molecule(smiles=mol_smiles))

        return mols


def decode_id(job_id: str, job_store_path=os.path.join(job_storage_path, 'all_jaguar_jobs.csv'), mol_store_path=mol_storage_path):
    try:
        components = job_id.split('_')
        assert components[0][0] == 'J'

        job_type = JobTypes.from_code(int(components[0][-1]))
        mol_ids = components[1].split('.')
    except AssertionError:
        print('job_id is not valid')
        return

    dft_method_code, dft_basis_code = [int(i) for i in components[2]]

    mols = tuple(retrieve_mols(mol_ids, mol_store_path))

    try:
        _, job_status = retrieve_job(job_id, job_store_path)
    except AssertionError:
        job_status = JobStatus.PENDING

    return JaguarJob(
        mols=mols,
        store_path=job_store_path,
        job_type=job_type,
        job_status=job_status,
        dft_method=DFTMethods.from_code(dft_method_code),
        dft_basis=DFTBases.from_code(dft_basis_code)
    )


class JaguarJob:
    def __init__(
        self,
        mols: tuple[mol.Molecule, ...] = (),
        store_path=os.path.join(job_storage_path, 'all_jaguar_jobs.csv'),
        job_type=JobTypes.UNSPECIFIED,
        job_status=JobStatus.PENDING,
        dft_method=DFTMethods.B3LYP.value,
        dft_basis=DFTBases.GAUSS_6_31_SS.value
    ):
        self.store_path = store_path
        self.type = job_type
        self.molecules = mols
        self.status = job_status
        self.id = self.encode_id()
        self.dft_method = dft_method
        self.dft_basis = dft_basis
        self.structure = ''

    def __repr__(self):
        return ('JaguarJob(job_id=%r, store_path=%r)'
            % (
                self.id,
                self.store_path
                ))

    def change_status(self, new_status: JobStatus):
        self.status = new_status

    def encode_id(self) -> str:
        job_id = f"J{self.type.value}"

        return job_id

    def is_new(self) -> bool:
        """
        Checks if the job has been previously created.

        :return: True if the job has not been created.
        """
        all_jobs = pd.read_csv(self.store_path)
        return self.id in all_jobs[JobInfo.JOB_ID.value].values

    def write_input(self) -> str:
        jaguar_method = self.dft_method.jaguar_name
        jaguar_basis = self.dft_basis.jaguar_name

        input_content = f"{JaguarInputParams.HEADER}\n"
        input_content += f"{JaguarInputParams.BASIS}={jaguar_basis}\n"
        input_content += f"{JaguarInputParams.DFT_NAME}={jaguar_method}\n"
        input_content += "&\n"
        input_content += f"{JaguarInputParams.ENTRY_NAME}={self.id}.in\n"
        input_content += f"{JaguarInputParams.Z_MAT}\n"
        input_content += f"{self.structure}\n"
        input_content += "&"

        return input_content

    # def store_id(self):


class JaguarOptimization(JaguarJob):
    def __init__(
        self,
        mols: tuple[mol.Molecule] = (),
        store_path=os.path.join(job_storage_path, 'all_jaguar_jobs.csv'),
        dft_method=DFTMethods.B3LYP_D3.value,
        dft_basis=DFTBases.GAUSS_6_31_SS.value,
        job_status=JobStatus.PENDING,
        job_type=JobTypes.OPT,
        igeopt=1,
        ifreqs=0
    ):
        super().__init__(mols=mols, store_path=store_path, job_type=job_type, job_status=job_status, dft_method=dft_method,
                         dft_basis=dft_basis)
        self.igeopt = igeopt
        self.ifreqs = ifreqs

    def __repr__(self):
        return 'JaguarOptimization(job_id=%r, store_path=%r, method)' % (self.id, self.store_path)

    def write_input(self) -> str:
        super_input = super().write_input()
        lines = super_input.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(f"{JaguarInputParams.BASIS}="):
                basis_line_index = i
                break

        # Insert the new lines at the correct position
        lines.insert(basis_line_index + 1, f"{JaguarInputParams.IGEOPT}=1")
        if self.ifreqs:
            lines.insert(basis_line_index + 3, f"{JaguarInputParams.IFREQ}=1")

        # Join the lines back into a single string
        content = '\n'.join(lines)
        return content


class JaguarTSOptimization(JaguarOptimization):
    def __init__(
        self,
        mols: tuple[mol.Molecule] = (),
        store_path=os.path.join(job_storage_path, 'all_jaguar_jobs.csv'),
        dft_method=DFTMethods.B3LYP_D3.value,
        dft_basis=DFTBases.GAUSS_6_31_SS.value,
        job_type=JobTypes.TS_OPT,
        job_status=JobStatus.PENDING,
        igeopt=2,  # *** the defining property of a TS Optimization
        ifreqs=0,
    ):
        super().__init__(mols=mols, store_path=store_path, dft_method=dft_method, dft_basis=dft_basis, job_status=job_status,
                         job_type=job_type, igeopt=igeopt, ifreqs=ifreqs)


class JaguarRCScan(JaguarOptimization):
    def __init__(
        self,
        scan_start: float,
        scan_end: float,
        scan_n_steps: int,
        mols: tuple[mol.Molecule] = (),
        store_path=os.path.join(job_storage_path, 'all_jaguar_jobs.csv'),
        dft_method=DFTMethods.B3LYP_D3.value,
        dft_basis=DFTBases.GAUSS_6_31_SS.value,
        job_type=JobTypes.RC_SCAN,
        job_status=JobStatus.PENDING,
        scan_atoms: tuple[Chem.Atom] = (),
        scan_type=RCScanTypes.DISTANCE,
        igeopt=1,
        ifreqs=0,
        n_steps=10
    ):
        super().__init__(mols=mols, store_path=store_path, dft_method=dft_method, dft_basis=dft_basis, job_status=job_status,
                         job_type=job_type, igeopt=igeopt, ifreqs=ifreqs)
        self.n_steps = n_steps
        self.scan = RCScan(mols[0], scan_atoms, scan_start, scan_end, scan_n_steps, scan_type)

    def write_input(self) -> str:
        scan_lines = f"{JaguarInputParams.ZVAR}\n"
        # NEEDS WORK
        scan_lines += '&\n'
        scan_lines += f"{JaguarInputParams.COORD}\n"
        # NEEDS WORK
        scan_lines += '&'

        return super().write_input() + '\n' + scan_lines


job = JaguarOptimization()
print(job.write_input())
