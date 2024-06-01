#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_510.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_510.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_10021_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10021_2111/J1_10021_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10022_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10022_2111/J1_10022_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10023_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10023_2111/J1_10023_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10025_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10025_2111/J1_10025_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10026_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10026_2111/J1_10026_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10027_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10027_2111/J1_10027_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10028_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10028_2111/J1_10028_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10030_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10030_2111/J1_10030_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10031_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10031_2111/J1_10031_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10032_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10032_2111/J1_10032_2111.in