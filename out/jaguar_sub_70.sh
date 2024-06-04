#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_70.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_70.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_5772_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_5772_3111/J1_5772_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_6815_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_6815_3111/J1_6815_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10143_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10143_3111/J1_10143_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10323_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10323_3111/J1_10323_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9867_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9867_3111/J1_9867_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9882_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9882_3111/J1_9882_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10404_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10404_3111/J1_10404_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10149_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10149_3111/J1_10149_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9971_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9971_3111/J1_9971_3111.in