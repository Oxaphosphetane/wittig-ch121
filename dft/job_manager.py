from job import *
import molecule as mol
from typing import List
from job_utils import JsonParser
import subprocess

from dft_parameters import DFTBases, DFTMethods
from slurm_manager import jaguar_sub, create_slurm_submission_script


class JobManager:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.job_counter = 0
        self.jobs = []

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
                    ifreqs=int(calculate_vibrational_energies)
                )
                self.job_counter += 1
                jobs.append(job)
            except Exception as e:
                print(e)

        return jobs

    """
    input: list of smiles strings
    loop through strings and create list of jobs.
    Loop through jobs
        - create job directory
        - create .in file in job directory
        
        Create sub file
        - define resources 
        - add jaguar run commands              
    """


# Main workflow
def main():
    # Step 1: Extract unique molecules from JSON
    json_parser = JsonParser(os.path.join(os_nav.find_project_root(), 'data', 'all_dfs.json'))
    unique_molecules = json_parser.get_unique_molecules()

    # for testing
    for category in unique_molecules:
        unique_molecules[category] = unique_molecules[category][:5]

    # Step 2: Create Jaguar jobs
    job_manager = JobManager(os.path.join(os_nav.find_project_root(), 'out'))
    all_jobs = []
    for category in unique_molecules:
        molecules = []
        if 'pdt' in category:
            mol_cls = mol.Oxaphosphetane
            source = os.path.join(os_nav.find_project_root(), 'data', 'mols', 'oxaphosphetanes.csv')
        else:
            mol_cls = mol.Molecule
            source = os.path.join(os_nav.find_project_root(), 'data', 'mols', 'wittig_reactants.csv')

        for m in unique_molecules[category]:
            print(m)
            try:
                molecules.append(mol_cls(m, source=source))
            except Exception as e:
                print(e)
                print()

        jobs = job_manager.create_jobs(molecules, job_type=JobTypes.OPT, dft_basis=DFTBases.GAUSS_6_31_SS.value, dft_method=DFTMethods.PBE_D3.value, calculate_vibrational_energies=True)
        all_jobs.extend(jobs)

    new_jobs = []
    for job in all_jobs:
        old_jobs = pd.read_csv(os.path.join(os_nav.find_project_root(), 'data', 'jobs', 'all_jaguar_jobs.csv'))
        if job.id in old_jobs['job_id'].values:
            continue

        new_jobs.append(job)
        new_job = pd.DataFrame({'job_id': [job.id], 'job_status': [job.status.value]})
        pd.concat([old_jobs, new_job], ignore_index=True).to_csv(os.path.join(os_nav.find_project_root(), 'data', 'jobs', 'all_jaguar_jobs.csv'), index=False)

        # make directory and in_file
        directory_path = os.path.join(os_nav.find_project_root(), 'out', f"{job.id}")
        os.makedirs(directory_path, exist_ok=True)

        with open(os.path.join(directory_path, f"{job.id}.in"), 'w') as in_file:
            in_file.write(job.write_input())
            in_file.close()

    batch_size = 10
    for i in range(0, len(new_jobs), batch_size):
        batch = new_jobs[i: min(len(new_jobs), i + batch_size)]
        job_paths = [os.path.join(os_nav.find_project_root(), 'out', job.id, f"{job.id}.in") for job in batch]
        script_path = create_slurm_submission_script(input_files=job_paths, script_path=os.path.join(os_nav.find_project_root(), 'out', f"jaguar_sub_{i}.sh"), cores=8, memory='2G', walltime='24:00:00')

        subprocess.run(['sbatch', script_path])


if __name__ == "__main__":
    main()
