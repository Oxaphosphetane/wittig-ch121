from job_manager import JaguarJob, JaguarOptimization
import slurm_manager

import os_navigation as os_nav

import os

job_list = [JaguarJob()]

for job in job_list:
    job_dir_path = os.path.join(os_nav.find_hpc_root(), 'wittig-ch121', job.id)
    os.makedirs(job_dir_path, exist_ok=True)

    in_file_name = f"{job.id}.in"

    with open(os.path.join(job_dir_path, in_file_name), 'w') as in_file:
        in_file.write(job.write_input())
        in_file.close()

    with open(os.path.join(job_dir_path, "jaguar.sub"), 'w') as sub_file:
        sub_file.write(slurm_manager.jaguar_sub(job_path=in_file_name, job_name=job.id))
        sub_file.close()



