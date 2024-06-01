#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "Job1"
#SBATCH --export=ALL
## /SBATCH -p general # partition (queue)
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_160.sh/slurm.%N.%j.out # STDOUT
## /SBATCH -o /central/home/labounad/wittig-ch121/out/jaguar_sub_160.sh/slurm.%N.%j.err # STDERR
cd /central/home/labounad/wittig-ch121/out/J1_770_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_770_2111/J1_770_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_8886_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_8886_2111/J1_8886_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_2481_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_2481_2111/J1_2481_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_1726_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_1726_2111/J1_1726_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_2408_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_2408_2111/J1_2408_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_2017_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_2017_2111/J1_2017_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_3528_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_3528_2111/J1_3528_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_9608_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_9608_2111/J1_9608_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_2924_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_2924_2111/J1_2924_2111.in
cd /central/home/labounad/wittig-ch121/out/J1_7773_2111
/groups/wag/programs/Schrodinger_2020_3/jaguar run -WAIT -PARALLEL 8 /central/home/labounad/wittig-ch121/out/J1_7773_2111/J1_7773_2111.in