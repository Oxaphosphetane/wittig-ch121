#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_30.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_30.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_9695_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9695_3111/J1_9695_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10196_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10196_2111/J1_10196_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_9930_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9930_3111/J1_9930_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9645_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9645_3111/J1_9645_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_9859_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9859_3111/J1_9859_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10519_3111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10519_3111/J1_10519_3111.in
cd /central/home/labounad/wittig-ch121/out/J1_10105_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_10105_2111/J1_10105_2111.in