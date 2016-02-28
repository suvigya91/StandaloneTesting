#!/bin/sh

#BATCH -J BlackboxTest
#SBATCH -o /home1/03894/tg831932/StandaloneTest/Output/BlackboxTest.out
#SBATCH -e /home1/03894/tg831932/StandaloneTest/Output/STDERR
#SBATCH -n 1
#SBATCH -p development
#SBATCH -t 00:10:00
#SBATCH --mail-user=suvigya91@gmail.com
#SBATCH --mail-type=begin
#SBATCH --mail-type=end


### amber testing ###

## ENVIRONMENT

## EXEC
module load TACC
module load intel/13.0.2.146
module load python/2.7.9
module load netcdf/4.3.2
module load hdf5/1.8.13


ibrun /opt/apps/intel13/mvapich2_1_9/amber/12.0/bin/sander -O -i ${HOME}/StandaloneTest/user_input/min.in -o ${HOME}/StandaloneTest/Output/min1.out -inf ${HOME}/StandaloneTest/user_input/min1.inf -r ${HOME}/StandaloneTest/user_input/md1.crd -p ${HOME}/StandaloneTest/user_input/penta.top -c ${HOME}/StandaloneTest/user_input/penta.crd -ref ${HOME}/StandaloneTest/user_input/min1.crd 
