from jaguar_job import *
import molecule as mol
from typing import List
from job_utils import JsonParser, JobTypes
import subprocess
import math

from dft_parameters import DFTBases, DFTMethods
from slurm_manager import jaguar_sub, create_slurm_submission_script

from config import Config, ConfigKeys

config = Config()


class JobManager:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.job_counter = 0
        self.jobs = []

    def build_molecule_list(
            self,
            data_path
    ):
        # Step 1: Extract unique molecules from JSON
        json_parser = JsonParser(data_path)
        unique_molecules = json_parser.get_unique_molecules()

        molecules = []
        for category in unique_molecules:
            mol_cls = mol.Molecule
            if 'pdt' in category:
                mol_cls = mol.Oxaphosphetane
                mol_type = mol.MoleculeType.OXAPHOSPHETANE
            elif 'ylide' in category:
                mol_type = mol.MoleculeType.YLIDE
            elif 'ald' in category:
                mol_type = mol.MoleculeType.CARBONYL
            else:
                mol_type = mol.MoleculeType.UNCATEGORIZED

            for m in unique_molecules[category]:
                try:
                    molecules.append(
                        mol_cls(m, type=mol_type, source=config.get_file(ConfigKeys.MOLECULES)))
                except Exception as e:
                    print(m)
                    print(e)
                    print()

        return molecules

    def create_jobs(
            self,
            molecules: List[mol.Molecule],
            job_type: JobTypes,
            dft_method: DFTMethods = DFTMethods.B3LYP_D3,
            dft_basis: DFTBases = DFTBases.GAUSS_6_31_SS,
            calculate_vibrational_energies: bool = False
    ) -> List[JaguarJob]:
        job_cls = globals()[job_type.value.jaguar_class_name]

        jobs = []
        for molecule in molecules:
            try:
                job = job_cls(
                    mols=(molecule,),
                    dft_method=dft_method,
                    dft_basis=dft_basis,
                    ifreq=int(calculate_vibrational_energies)
                )
                self.job_counter += 1
                jobs.append(job)
            except Exception as e:
                print(e)

        return jobs

    @staticmethod
    def estimate_job_runtime(job: JaguarJob) -> float:
        """

        :param job:
        :return: estimated runtime for job in seconds
        """
        if job.dft_method.runtime_estimator is not None:
            estimator = job.dft_method.runtime_estimator
        else:
            estimator = DFTMethods.PBE_D3.value.runtime_estimator

        n_atoms = 0
        for m in job.molecules:
            n_atoms += m.molecule_with_hydrogens.GetNumAtoms()

        return estimator(n_atoms)

    def setup_job_dir(self, job, overwrite=False):
        # make directory and in_file
        job_dir = os.path.join(self.output_dir, f"{job.id}")

        if not overwrite:
            if os.path.isdir(job_dir):
                return

        os.makedirs(job_dir, exist_ok=True)
        with open(os.path.join(job_dir, f"{job.id}.in"), 'w') as in_file:
            in_file.write(job.write_input())
            in_file.close()

    def setup_job_dirs(self, jobs, overwrite=False):
        for job in jobs:
            self.setup_job_dir(job, overwrite=overwrite)

    def sbatch_jobs(self, job_list: List[JaguarJob], batch_size: int = 10):
        """
        Distribute jobs into batches that have roughly the same total estimated runtimes and submits them)

        :param job_list: List of JaguarJob objects.
        :param batch_size: The number of jobs per batch.
        :return: List of batches, where each batch is a list of jobs.
        """
        # Calculate the number of batches
        n_batches = math.ceil(len(job_list) / batch_size)

        # Estimate the runtime for each job
        job_runtimes = [(job, self.estimate_job_runtime(job)) for job in job_list]

        # Initialize the batches
        batches = [[] for _ in range(n_batches)]
        batch_runtimes = [0] * n_batches

        # Sort jobs by estimated runtime in descending order
        job_runtimes.sort(key=lambda x: x[1], reverse=True)

        # Distribute the jobs into batches
        for job, runtime in job_runtimes:
            # Find the batch with the minimum total runtime
            min_batch_index = batch_runtimes.index(min(batch_runtimes))
            # Add the job to this batch
            batches[min_batch_index].append(job)
            # Update the total runtime of this batch
            batch_runtimes[min_batch_index] += runtime

        for i, batch in enumerate(batches):
            batch.reverse()
            job_paths = [os.path.join(os_nav.find_project_root(), 'out', job.id, f"{job.id}.in") for job in batch]
            script_path = create_slurm_submission_script(
                input_files=job_paths,
                script_path=os.path.join(os_nav.find_project_root(), 'out', f"jaguar_sub_{i}.sh"),
                cores=config.get_hpc_resource(ConfigKeys.CORES),
                memory=config.get_hpc_resource(ConfigKeys.MEMORY),
                walltime=config.get_hpc_resource(ConfigKeys.WALLTIME)
            )

            subprocess.run(['sbatch', script_path])

        return batches


def main():
    job_manager = JobManager(config.get_file(ConfigKeys.OUT_DIR))
    molecules = job_manager.build_molecule_list(data_path=config.get_file(ConfigKeys.MOLECULE_SOURCE))

    path_to_job_tracker = config.get_file(ConfigKeys.JOB_TRACKER)
    batched_jobs = pd.read_csv(path_to_job_tracker)

    job_type = JobTypes.from_name(config.get_job_spec(ConfigKeys.JOB_TYPE))
    failed_jobs = batched_jobs[batched_jobs[JobInfo.JOB_STATUS.value] == JobStatus.ERROR.value]
    finished_jobs = batched_jobs[batched_jobs[JobInfo.JOB_STATUS.value] == JobStatus.FINISHED.value]

    def mol_id_extractor(s):
        return int(s.split('_')[1])

    failed_mol_ids = failed_jobs[JobInfo.JOB_ID.value].map(mol_id_extractor).tolist()
    finished_mol_ids = finished_jobs[JobInfo.JOB_ID.value].map(mol_id_extractor).tolist()

    dft_basis = DFTBases.GAUSS_6_31_SS.value
    failed_mols = []
    finished_mols = []
    not_run_mols = []
    for m in molecules:
        mol_id = m.id
        try:
            coordinates_path = os.path.join(config.get_file(ConfigKeys.OUT_DIR), f"J1_{mol_id}_2111",
                                            f"J1_{mol_id}_2111.01.in")
            try:
                m.add_coordinates_from_file(coordinates_path)
            except FileNotFoundError:
                not_run_mols.append(m)
                continue
            if mol_id in failed_mol_ids:
                failed_mols.append(m)
            elif mol_id in finished_mol_ids:
                finished_mols.append(m)
            else:
                not_run_mols.append(m)
        except Exception as e:
            print(e)
            print()

    first_run_jobs = job_manager.create_jobs(
        molecules=not_run_mols, job_type=job_type, dft_basis=dft_basis, dft_method=DFTMethods.PBE_D3.value,
        calculate_vibrational_energies=True)

    print('first_run_jobs created')

    new_jobs = job_manager.create_jobs(
        molecules=failed_mols, job_type=job_type, dft_basis=dft_basis, dft_method=DFTMethods.PBE_D3.value,
        calculate_vibrational_energies=True)
    print('failed jobs resume created')
    new_jobs.extend(job_manager.create_jobs(
        molecules=finished_mols, job_type=job_type, dft_basis=dft_basis, dft_method=DFTMethods.B3LYP_D3.value,
        calculate_vibrational_energies=True
    ))
    print('finished mols new jobs created')

    job_manager.setup_job_dirs(new_jobs, overwrite=True)
    job_manager.setup_job_dirs(first_run_jobs, overwrite=False)

    print('job directories setup')

    new_jobs.extend(first_run_jobs)

    job_manager.sbatch_jobs(new_jobs, batch_size=config.get_job_spec(ConfigKeys.BATCH_SIZE))


if __name__ == "__main__":
    main()

    # smi = "CC/C=C/C=P(c1ccccc1)(c1ccccc1)c1ccccc1"
    # mol_id = 414
    # job_id = f"J1_{mol_id}_2111"
    # m = mol.Molecule(
    #     smi,
    #     source=config.get_file(ConfigKeys.MOLECULES),
    #     type=mol.MoleculeType.CARBONYL,
    #     coordinates_path=os.path.join(config.get_file(ConfigKeys.OUT_DIR), job_id, f'{job_id}.01.in')
    # )
    #
    # print(m.id)
    # print(m.scrape_coordinates(os.path.join(config.get_file(ConfigKeys.OUT_DIR), job_id, f'{job_id}.in')))
    # m.visualize_3d(label=f'{job_id}.in')
    #
    # # Retrieve the first conformer (ID is 0 by default for the first conformer)
    # conf = m.molecule_with_hydrogens.GetConformer(0)
    #
    # # Print positions of atoms in the conformer
    # for i in range(m.molecule_with_hydrogens.GetNumAtoms()):
    #     pos = conf.GetAtomPosition(i)
    #     print(f"Atom {i}: x={pos.x}, y={pos.y}, z={pos.z}")
    #
    # for atom in m.molecule_with_hydrogens.GetAtoms():
    #     # Get the atomic number of the atom
    #     atomic_num = atom.GetAtomicNum()
    #     # Get the symbol of the atom
    #     symbol = atom.GetSymbol()
    #     # Get the index of the atom
    #     index = atom.GetIdx()
    #     # Print atom information
    #     print(f"Atom index: {index}, Atomic number: {atomic_num}, Symbol: {symbol}")