#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_80.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_80.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_923_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_923_3111/J1_923_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9773_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9773_3111/J1_9773_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9993_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9993_3111/J1_9993_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10090_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10090_3111/J1_10090_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10452_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10452_3111/J1_10452_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10563_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10563_3111/J1_10563_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9968_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9968_3111/J1_9968_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10053_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10053_3111/J1_10053_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10084_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10084_3111/J1_10084_3111.in