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


### coco testing ###

## ENVIRONMENT
export PYTHONPATH=/opt/apps/intel13/mvapich2_1_9/python/2.7.9/lib/python2.7/site-packages:/work/02998/ardi/coco_installation/lib/python2.7/site-packages:$PYTHONPATH
export PATH=/work/02998/ardi/coco_installation/bin:$PATH

## EXEC
module load TACC
module load intel/13.0.2.146
module load python/2.7.9
module load netcdf/4.3.2
module load hdf5/1.8.13


ibrun pyCoCo --grid 5 --dims 3 --frontpoints 4 --topfile ${HOME}/StandaloneTest/user_input/penta.top --mdfile ${HOME}/StandaloneTest/user_input/*.ncdf --output ${HOME}/StandaloneTest/Output/pdbs --logfile ${HOME}/StandaloneTest/Output/coco.log --mpi --selection protein