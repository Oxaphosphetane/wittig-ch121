#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_210.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_210.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_6997_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_6997_2111/J1_6997_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_873_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_873_2111/J1_873_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_6476_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_6476_2111/J1_6476_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_1086_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_1086_2111/J1_1086_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_4578_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_4578_2111/J1_4578_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_5324_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_5324_2111/J1_5324_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_9749_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9749_2111/J1_9749_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_9770_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9770_2111/J1_9770_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_7739_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_7739_2111/J1_7739_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_4688_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_4688_2111/J1_4688_2111.in