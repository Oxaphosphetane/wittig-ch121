#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_30.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_30.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_4013_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_4013_2111/J1_4013_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_5526_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_5526_2111/J1_5526_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_7069_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_7069_2111/J1_7069_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_2934_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_2934_2111/J1_2934_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_9662_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9662_2111/J1_9662_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_2992_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_2992_2111/J1_2992_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_5860_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_5860_2111/J1_5860_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_9243_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9243_2111/J1_9243_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_4043_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_4043_2111/J1_4043_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_3114_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_3114_2111/J1_3114_2111.in