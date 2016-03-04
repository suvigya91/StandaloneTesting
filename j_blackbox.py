#jenkins script

import json
import os
import re
import subprocess
import time
import sys
import argparse
import imp
import glob
from os.path import expanduser

class Blackbox():
    def __init__(self,
                 name,
                 resource,
                 grid = 5,
                 dims = 3,
                 num_CUs = 4,
                 atom = 'protein'
                 ):
        self.pre_exec = []
        self.wdir = None
        self.wall_time_limit = None
        self.queue = None
        self.email = None
        self.environment = []
        self.uname = None
        self.exe = None
        self.kernel_name = name
        self.resource = resource
        self.job_id = None
        self.exitcode = None
        self.home = None
        self.grid = grid
        self.dims = dims
        self.num_CUs = num_CUs
        self.atom = atom

##        self.inp_file = [];
##        for f in inp_file.split(" "):
##            self.inp_file.append(f)


    def loadConfig(self):
        self.home = expanduser("~")
        try:
            with open('%s/workspace/StandaloneTest/configs/machine_config.json'%self.home) as data_file:
                config = json.load(data_file)

            if(self.kernel_name == "amber"):
                Kconfig = imp.load_source('Kconfig', './configs/amber.wcfg')
            elif(self.kernel_name == "coco"):
                Kconfig = imp.load_source('Kconfig', './configs/coco.wcfg')
            elif(self.kernel_name == "gromacs"):
                Kconfig = imp.load_source('Kconfig', './configs/gromacs.wcfg')
            elif(self.kernel_name == "lsdmap"):
                Kconfig = imp.load_source('Kconfig', './configs/lsdmap.wcfg')

            m_cfg = config["machine_configs"][self.resource]
            k_cfg = config["kernal_configs"][self.kernel_name]

            #-------------------------------------------------------
            #Machine configs
            self.wdir = m_cfg["working_dir"]
            self.wall_time_limit = m_cfg["wall_time"]
            self.email = m_cfg["email"]
            self.queue = m_cfg["queue"]
            self.uname = m_cfg["username"]

            #-------------------------------------------------------
            #Kernal config
            self.exe = k_cfg["executable"]
            self.pre_exec = Kconfig.stampede_module
            self.environment = Kconfig.stampede_environment
        except Exception:
            print 'error'
            raise


    def generateSlurm(self,stage):
        self.loadConfig()
        #print self.pre_exec

        #cwd = self.wdir
        pwd = "%s/StandaloneTest"%self.wdir
        job_name = "BlackboxTest"
        output = "BlackboxTest.out"
        error = None
        #wall_time_limit = self.wall_time_limit
        #queue = self.queue
        project = None
        #email = self.email
        #exe = self.exe
        #print cwd
        #print pwd
        slurm_script = "#!/bin/sh\n\n"

        slurm_script += '#BATCH -J %s\n' % job_name
        slurm_script += '#SBATCH -o /home1/03894/tg831932/StandaloneTest/Output/%s\n' % (output)
        slurm_script += '#SBATCH -e /home1/03894/tg831932/StandaloneTest/Output/STDERR\n'
        slurm_script += '#SBATCH -n 1\n'
        slurm_script += '#SBATCH -p %s\n' %self.queue
        slurm_script += '#SBATCH -t %s\n' % self.wall_time_limit
        slurm_script += '#SBATCH --mail-user=%s\n' % self.email
        slurm_script += '#SBATCH --mail-type=begin\n'
        slurm_script += '#SBATCH --mail-type=end\n'
        slurm_script += "\n\n### %s testing ###\n"%self.kernel_name
        
        slurm_script += "\n## ENVIRONMENT\n"
        for val in self.environment:
            slurm_script += "%s\n" % (val)

        
        slurm_script += "\n## EXEC\n"
        for mod in self.pre_exec:
            slurm_script += "%s\n" % mod

        #---------------------------------------------------------------------------------------------
        #test stage 1. Test for input modules
        if(stage == 0):
            if (self.kernel_name == "amber"): 
                print "Amber Batch File"
                slurm_script += "\n\nibrun %s -O -i %s/input/min.in -o %s/Output/min.out -inf %s/input/min.inf -r %s/input/md.crd -p %s/input/penta.top -c %s/input/penta.crd -ref %s/input/min.crd \n"\
                                                              %(self.exe, pwd, pwd, pwd,pwd,pwd, pwd,pwd)

            elif(self.kernel_name == "coco"):
                print "CoCo Batch file"
                slurm_script += "\n\nibrun %s --grid %s --dims %s --frontpoints %s --topfile %s/input/penta.top --mdfile %s/input/*.ncdf --output %s/Output/pdbs --logfile %s/Output/coco.log --mpi --selection %s" %(
                                                            self.exe, self.grid, self.dims, self.num_CUs, pwd,pwd,pwd,pwd,self.atom)


        #---------------------------------------------------------------------------------------------
        #test stage 2. Test for execution if module check is successful 
        if(stage == 1):
            if (self.kernel_name == "amber"): 
                print "Amber Batch File"
                slurm_script += "\n\nibrun %s -O -i %s/user_input/min.in -o %s/Output/min.out -inf %s/user_input/min.inf -r %s/user_input/md.crd -p %s/user_input/penta.top -c %s/user_input/penta.crd -ref %s/user_input/min.crd \n"\
                                                              %(self.exe, pwd, pwd, pwd,pwd,pwd, pwd,pwd)

            elif(self.kernel_name == "coco"):
                print "CoCo Batch file"
                slurm_script += "\n\nibrun %s --grid %s --dims %s --frontpoints %s --topfile %s/user_input/penta.top --mdfile %s/user_input/*.ncdf --output %s/Output/pdbs --logfile %s/Output/coco.log --mpi --selection %s" %(
                                                            self.exe, self.grid, self.dims, self.num_CUs, pwd,pwd,pwd,pwd,self.atom)

        return slurm_script


    def transferFile(self):
        #Transfer file to remote machine
        files = glob.glob('%s/workspace/StandaloneTest/Output/*'%self.home)
        for f in files:
            os.remove(f)
        
        print "Transferring files to remote machine"
        p = subprocess.Popen(['scp', '-r', '%s/workspace/StandaloneTest/'%self.home , '%s@stampede.tacc.utexas.edu:/%s'%(self.uname,self.wdir)],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print stderr
        for line in stderr.split("\n"):
            if line is "":
                print "Transferring successful"
            else:
                print "Transfer Failed"
                sys.exit(1)



    def job_submit(self):
        #Submit job
        print "Submitting slurm job"
        p = subprocess.Popen(['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'sbatch %s/StandaloneTest/slurm_script.slurm'%self.wdir],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
       # print stdout
        #job_id = None
        for line in stdout.split("\n"):
            if "Submitted batch job" in line:
                self.job_id = "%s" %int(line.split()[-1:][0])
                #print line
        if self.job_id!= None:
            print "Submission successful: Job id = ",self.job_id
        else:
            print "Submission failure"
            sys.exit(1)



    def job_check(self):
        #Check for job completion
        command = ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'squeue --job', self.job_id]
        #command = ['ssh','tg831932@stampede.tacc.utexas.edu','scontrol show job', job_id]
        state = None
        print "Waiting for code to execute..."
        while(state != "CG"):
            p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            #print stdout
            for line in stdout.split("\n"):
                if ("CG") in line:
                    state = "CG"
                    break
            time.sleep(3)
        print "Execution complete..."
        print "--------> %s <---------"%state



    def error_check(self):
        if(self.kernel_name == "amber" or self.kernel_name == "coco" or self.kernel_name == "lsdmap"):
            print "checking error in %s"%self.kernel_name
            p = subprocess.Popen(['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'cat %s/StandaloneTest/Output/STDERR'%self.wdir],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            #exitcode = 0
            
            for line in stdout.split("\n"):
                if (("error" in line) or ("Error" in line)):
                    self.exitcode = 1
                    #print "Execution Failed, Check STDERR. Exit Code= %s\n"%self.exitcode 
                    #print stdout
                    break

            if(self.exitcode != 1):
                command = ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'scontrol show job', self.job_id]
                p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                for line in stdout.split("\n"):
                    if "ExitCode=1" in line:
                        self.exitcode = 1
                        #print "Execution Failed, Check STDERR. Exit Code= %s"%self.exitcode 
                    elif "ExitCode=0" in line:
                        self.exitcode = 0
                        #print "Execution Successful. All the modules are loaded correctly. Exit code = %s"%self.exitcode



    def cleanup(self):
        #Transfer files from remote to local machine
        print "Transfer output to local machine"
        p = subprocess.Popen(['scp', '-r', '%s@stampede.tacc.utexas.edu:/%s/StandaloneTest/Output/'%(self.uname,self.wdir), '%s/workspace/StandaloneTest/'%self.home ],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        for line in stderr.split("\n"):
            if line is "":
                print "Transfer to local machine successful"
            else:
                print "Transfer Failed"

        #-----------------------------------------------------------------------------------------------------
        #Clean up remote machine
        command =  ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'chmod', '-R','a+rX','%s/StandaloneTest/'%self.wdir]
        p = subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        
        command =  ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'rm', '-r','%s/StandaloneTest/'%self.wdir]
        p = subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print "Removed all the files from remote machine"



    def run(self):
##        #-------------------------------------------------------------------------------------------------------
##        #check input args
##        if (self.kernel_name == 'amber' and len(self.inp_file) != 6):
##            print "Amber requires 6 files"
##            sys.exit(1)
##
##        elif(self.kernel_name == 'coco' and len(self.inp_file) != 6):
        #self.generateSlurm()
        #--------------------------------------------------------------------------------------------------------
        #Check if all modules are loaded correctly
        slurm_script = self.generateSlurm(0)
       
        target = open('slurm_script.slurm','w')
        target.write(slurm_script)
        target.close()

        self.transferFile()

        command =  ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'chmod', '-R','a+rX','%s/StandaloneTest/'%self.wdir]
        p = subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()


        self.job_submit()
        self.job_check()
        self.error_check()
        self.cleanup()
        if(self.exitcode == 1):
            print "Modules incorrectly loaded, check STDERR file. Also update configs/%s.wcfg"%self.kernel_name
            sys.exit(1)
        else:
            print "All the modules are loaded correctly."

        #---------------------------------------------------------------------------------------------------------
        #Check if the execution is successful
        print "\nChecking execution\n"
        self.exitcode = 0
        slurm_script = self.generateSlurm(1)
       
        target = open('slurm_script.slurm','w')
        target.write(slurm_script)
        target.close()

        self.transferFile()

        command =  ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'chmod', '-R','a+rX','%s/StandaloneTest/'%self.wdir]
        p = subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        self.job_submit()
        self.job_check()
        self.error_check()
        self.cleanup()
        if(self.exitcode == 1):
            print "Execution failed, Check STDERR file"
            sys.exit(1)
        else:
            print "The execution is successful, Check Output folder for output. All set to use EnsembleMD"
        
                 
