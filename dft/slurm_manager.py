import os
from typing import List


def create_slurm_submission_script(
        input_files: List,
        script_path: str,
        walltime: str = '72:00:00',
        cores=16,
        nodes=1,
        memory='4G'
) -> str:
    script_content = jaguar_sub(
        walltime=walltime,
        job_paths=input_files,
        cores=cores,
        nodes=nodes,
        memory=memory,
        outlog=os.path.join(script_path, 'slurm.%N.%j.out'),
        errlog=os.path.join(script_path, 'slurm.%N.%j.err')
    )
    with open(script_path, 'w') as file:
        file.write(script_content)
    return script_path


def jaguar_sub(
        walltime='24:00:00',
        cores=16,
        nodes=1,
        memory='4G',
        job_name='Job1',
        export='ALL',
        jaguar_path: str = '/groups/wag/programs/Schrodinger_2020_3/jaguar',
        job_paths: list[str] = None,
        outlog='slurm.%N.%j.out',
        errlog='slurm.%N.%j.err'
) -> str:
    run_commands = '\n'.join([f"cd {os.path.dirname(job_path)}\n{jaguar_path} run -WAIT -PARALLEL {cores} {job_path}" for job_path in job_paths])

    output = "#!/bin/bash\n"
    output += f"#SBATCH --time={walltime}\n"
    output += f"#SBATCH --ntasks={cores}\n"
    output += f"#SBATCH --nodes={nodes}\n"
    output += f"#SBATCH --mem-per-cpu={memory}\n"
    output += f'#SBATCH -J "{job_name}"\n'
    output += f"#SBATCH --export={export}\n"
    output += f"## /SBATCH -p general # partition (queue)\n"
    output += f"## /SBATCH -o {outlog} # STDOUT\n"
    output += f"## /SBATCH -o {errlog} # STDERR\n"
    output += run_commands

    return output

