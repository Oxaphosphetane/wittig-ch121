from dft_parameters import *
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

import os_navigation as os_nav
import enum
import pandas as pd

from rdkit import Chem
import molecule as mol

from collections import Counter

from job_utils import JobInfo, JobStatus

job_storage_path = os.path.join(os_nav.find_project_root(), 'data', 'jobs')
mol_storage_path = os.path.join(os_nav.find_project_root(), 'data', 'mols')


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


class Stereochem(enum.Enum):
    NO_STEREO = 'A'
    E = 0
    Z = 1
    R = 2
    S = 3


class JaguarJob:
    def __init__(
        self,
        mols: tuple[mol.Molecule, ...] = (),
        store_path=os.path.join(job_storage_path, 'all_jaguar_jobs.csv'),
        out_dir=os.path.join(os_nav.find_project_root(), 'out'),
        job_type=JobTypes.UNSPECIFIED,
        job_status=JobStatus.PENDING,
        dft_method=DFTMethods.B3LYP.value,
        dft_basis=DFTBases.GAUSS_6_31_SS.value,
        igeopt=0,
        ifreq=0
    ):
        self.store_path = store_path
        self.type = job_type
        self.molecules = mols
        self.status = job_status
        self.dft_method = dft_method
        self.dft_basis = dft_basis
        self.igeopt = igeopt
        self.ifreq = ifreq
        self.id = self.encode_id()
        self.coordinates = self._get_all_coordinates()
        self.out_path = os.path.join(out_dir, self.id)

    def __repr__(self):
        return ('JaguarJob(job_id=%r, store_path=%r)'
            % (
                self.id,
                self.store_path
                ))

    def set_status(self, new_status: JobStatus):
        self.status = new_status

    @staticmethod
    def _find_molecule_index(smiles: str, csv_path: str) -> int:
        """
        Finds the index of a given SMILES string in a CSV file.

        :param smiles: The SMILES string to search for.
        :param csv_path: The path to the CSV file.
        :return: The index number of the matching row or -1 if not found.
        """
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_path)

        # Search for the SMILES string in the smiles column
        matching_row = df[df['smiles'] == smiles]

        if not matching_row.empty:
            # Return the index of the matching row
            return matching_row.index[0]
        else:
            # Return -1 if the SMILES string is not found
            return -1

    def _id_mol_component(self) -> str:
        smis = [JaguarJob._find_molecule_index(Chem.MolToSmiles(m, isomericSmiles=True), m.source) for m in self.molecules]

    def encode_id(self) -> str:
        job_id = f"J{self.type.value.code}_{'.'.join([str(mol.id) for mol in self.molecules])}_{self.dft_method.code}{self.dft_basis.code}"
        return job_id

    def is_new(self) -> bool:
        """
        Checks if the job has been previously created.

        :return: True if the job has not been created.
        """
        all_jobs = pd.read_csv(self.store_path)
        return self.id not in all_jobs[JobInfo.JOB_ID.value].values

    def _get_all_coordinates(self):
        atom_coords = []
        for mol in self.molecules:
            idx_start = len(atom_coords) + 1  # change from 0-indexing to 1-indexing for Jaguar
            atom_coords.append(mol.export_conformer_coordinates(idx_start=idx_start))
        return '\n'.join(atom_coords)

    def write_input(self) -> str:
        jaguar_method = self.dft_method.jaguar_name
        jaguar_basis = self.dft_basis.jaguar_name

        input_content = f"{JaguarInputParams.HEADER}\n"
        input_content += f"{JaguarInputParams.BASIS}={jaguar_basis}\n"
        input_content += f"{JaguarInputParams.DFT_NAME}={jaguar_method}\n"
        input_content += "&\n"
        input_content += f"{JaguarInputParams.ENTRY_NAME}: {self.id}.in\n"
        input_content += f"{JaguarInputParams.Z_MAT}\n"
        input_content += f"{self.coordinates}\n"
        input_content += "&\n\n"  # for some reason needs a empty line at end of file if ifreq=1, and a single \n does not produce an empty line

        return input_content

    def store(self):
        try:
            JaguarJob.retrieve_job(self.id, self.store_path)
            return
        except AssertionError:
            new_job = {
                JobInfo.JOB_ID.value: self.id,
                JobInfo.JOB_STATUS.value: self.status.value
            }
            df = pd.read_csv(self.store_path)
            df = df.append(new_job, ignore_index=True)
            df.to_csv(self.store_path, index=False)

    @staticmethod
    def retrieve_job(job_id: str, store_path: str) -> tuple:
        jobs = pd.read_csv(store_path)

        if job_id not in jobs[JobInfo.JOB_ID.value].values:
            raise ValueError(f"Job ID {job_id} not found in the job store.")

        retrieved_job = jobs[jobs[JobInfo.JOB_ID.value] == job_id]
        job_tuple = tuple(retrieved_job.iloc[0])

        return job_tuple

    @staticmethod
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
                mol_container = os.path.join(store_path, 'wittig_molecules.csv')
                idx = mol_id
                qty = 1

            for i in range(int(qty)):
                container = pd.read_csv(mol_container, index_col=0)
                mol_smiles = container.loc[idx, 'smiles']
                mols.append(mol.Molecule(smiles=mol_smiles, source=mol_container))

        return mols

    @staticmethod
    def decode_id(job_id: str, job_store_path=os.path.join(job_storage_path, 'all_jaguar_jobs.csv'), mol_store_path=mol_storage_path) -> dict:
        try:
            components = job_id.split('_')
            assert components[0][0] == 'J'

            job_type = JobTypes.from_code(int(components[0][-1]))
            mol_ids = components[1].split('.')
        except AssertionError:
            raise ValueError('job_id is not valid')

        dft_method_code, dft_basis_code = [int(i) for i in components[2][:2]]

        mols = tuple(JaguarJob.retrieve_mols(mol_ids, mol_store_path))

        try:
            _, job_status = JaguarJob.retrieve_job(job_id, job_store_path)
        except ValueError:
            job_status = JobStatus.PENDING

        return {
            "test_mols": mols,
            "store_path": job_store_path,
            "job_type": job_type,
            "job_status": job_status,
            "dft_method": DFTMethods.from_code(dft_method_code),
            "dft_basis": DFTBases.from_code(dft_basis_code)
        }
        return

    @classmethod
    def from_id(cls, job_id: str):
        job_info = cls.decode_id(job_id)
        return cls(
            mols=job_info["test_mols"],
            store_path=job_info["store_path"],
            job_type=job_info["job_type"],
            job_status=job_info["job_status"],
            dft_method=job_info["dft_method"],
            dft_basis=job_info["dft_basis"]
        )


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
        ifreq=0
    ):
        super().__init__(mols=mols, store_path=store_path, job_type=job_type, job_status=job_status,
                         dft_method=dft_method, dft_basis=dft_basis, igeopt=igeopt, ifreq=ifreq)

    def __repr__(self):
        return 'JaguarOptimization(job_id=%r, store_path=%r, method)' % (self.id, self.store_path)

    def encode_id(self) -> str:
        base_id = super().encode_id()
        return base_id + f"{self.igeopt}{self.ifreq}"

    def write_input(self) -> str:
        super_input = super().write_input()
        lines = super_input.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(f"{JaguarInputParams.BASIS}="):
                basis_line_index = i
                break

        # Insert the new lines at the correct position
        lines.insert(basis_line_index + 1, f"{JaguarInputParams.IGEOPT}=1")
        if self.ifreq:
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
        ifreq=0,
    ):
        super().__init__(mols=mols, store_path=store_path, dft_method=dft_method, dft_basis=dft_basis,
                         job_status=job_status, job_type=job_type, igeopt=igeopt, ifreq=ifreq)


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
        ifreq=0,
        n_steps=10
    ):
        super().__init__(mols=mols, store_path=store_path, dft_method=dft_method, dft_basis=dft_basis,
                         job_status=job_status, job_type=job_type, igeopt=igeopt, ifreq=ifreq)
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


# test_mols = (mol.Molecule('C=CCC/C=C/[C@@H](O[Si](C)(C)C(C)(C)C)[C@H](C)/C=C(\C)C=O', source=os.path.join(os_nav.find_project_root(), 'data', 'mols', 'wittig_molecules.csv')),)
# job = JaguarOptimization(ifreq=1, dft_basis=DFTBases.DEF2_TZVP_F.value, dft_method=DFTMethods.B3LYP_D3.value, mols=test_mols)
# print(job.type.value.job_type)
# with open('lol.in', 'w') as file:
#     file.write(job.write_input())
#     file.close()
# print(job.write_input())

