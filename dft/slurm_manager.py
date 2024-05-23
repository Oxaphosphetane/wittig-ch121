

def jaguar_sub(
        walltime='24:00:00',
        cores=16,
        nodes=1,
        memory='4G',
        job_name='Job1',
        export='ALL',
        jaguar_path: str = '/groups/wag/programs/Schrodinger_2020_3/jaguar',
        job_path: str = '',
        outlog='slurm.%N.%j.out',
        errlog='slurm.%N.%j.err'
) -> str:
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
    output += f"{jaguar_path} run -WAIT -PARALLEL {cores} {job_path}"

    return output
