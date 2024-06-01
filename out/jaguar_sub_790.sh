#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_790.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_790.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_10333_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10333_2111/J1_10333_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10334_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10334_2111/J1_10334_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10335_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10335_2111/J1_10335_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10336_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10336_2111/J1_10336_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10337_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10337_2111/J1_10337_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10338_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10338_2111/J1_10338_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10339_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10339_2111/J1_10339_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10340_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10340_2111/J1_10340_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10341_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10341_2111/J1_10341_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_10342_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10342_2111/J1_10342_2111.in