
"""
Tool to test the proper loading of Supercomputer specific environments, modules
and input files. Checks the execution in 3 phases:
1. Check for proper initialization of tool
2. Check for proper modules and environment on Supercomputer
3. Check for complete execution with user input files
"""

import json
import os
import re
import subprocess
import time
import sys
import argparse
import imp
import glob
import shutil
from colorama import *

from shutil import copyfile
from os.path import expanduser

LOCAL_HOME = '/home/suvigya/Standalone'

class Standalone():
    def __init__(self,
                 name,
                 resource,
                 arguments,
                 modules = None
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
        self.inp_file = arguments
        self.output_file = None
        self.user_modules = modules

    ###################################################################################################
    def copyFilesToRemote(self, inp_files, stage, module):
        #-------------------------------------------------------------------------------------------------
        #transfer in-built input files for module check stage
        if(stage == 0):
            target = open('module_error.log','w')
            test_mod = ""
            #if self.user_modules is None:
            for mod in module:
                test_mod += "%s\n"%mod
                #print "Testing ",test_mod
            p = subprocess.Popen(['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'%s'%test_mod],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            target.write(stderr)
            target.write('\n\n')
            for line in stderr.split("\n"):
                if (("error" in line) or ("Error" in line)):
                    print(Fore.RED+"Module loading error, Check module_error file and add modules explicitly!!"+Fore.RESET)
                    sys.exit(1)

            print(Fore.GREEN+"Modules loaded correctly"+Fore.RESET)
            target.close()

        #-------------------------------------------------------------------------------------------------
        #Copy user input files for checking at stage 2
        if(stage == 1):
            #-------------------------------------------------------------------------------------------------
            #Create directories
            p = subprocess.Popen(['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'mkdir -p Standalone/Output'])
            stdout, stderr = p.communicate()
    
            p = subprocess.Popen(['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'mkdir -p Standalone/user_files'])
            stdout, stderr = p.communicate()

            for f in inp_files:
                #Transfer files without argument
                if ('=' not in f and '/' in f):
                    p = subprocess.Popen(['scp','%s'%f , '%s@stampede.tacc.utexas.edu:/%s/Standalone/user_files'%(self.uname,self.wdir)],
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                    stdout, stderr = p.communicate()
                    if stderr is "":
                        print(f+' transferred')
                
                elif '=' in f:
                    #transfer file with argument
                    argument,fname = f.split('=')
                    if not fname.isdigit():
                        p = subprocess.Popen(['scp','%s'%fname , '%s@stampede.tacc.utexas.edu:/%s/Standalone/user_files'%(self.uname,self.wdir)],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                        stdout, stderr = p.communicate()
                        if stderr is "":
                            print fname, 'transferred'

                        if "*" in fname:
                            for files in glob.glob(fname):
                                #print files
                                p = subprocess.Popen(['scp','%s'%files , '%s@stampede.tacc.utexas.edu:/%s/Standalone/user_files'%(self.uname,self.wdir)],
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
                                stdout, stderr = p.communicate()
                                if stderr is "":
                                    print(files+' transferred')

            p = subprocess.Popen(['scp', '%s/slurm_script.slurm'%LOCAL_HOME , '%s@stampede.tacc.utexas.edu:/%s/Standalone/'%(self.uname,self.wdir)],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()


    ###################################################################################################
    def generateSlurm(self,inp_files):
        self.loadConfig()

        pwd = "%s/Standalone"%self.wdir
        job_name = "BlackboxTest"
        output = "BlackboxTest.out"
        error = None
        project = None

        slurm_script = "#!/bin/sh\n\n"
        slurm_script += '#BATCH -J %s\n' % job_name
        slurm_script += '#SBATCH -o /home1/03894/tg831932/Standalone/Output/%s\n' % (output)
        slurm_script += '#SBATCH -e /home1/03894/tg831932/Standalone/Output/STDERR\n'
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

        #print "Execution test"
        slurm_script += "\n\nibrun %s "%self.exe

        for f in inp_files:
            if (('=' not in f) and ('/' not in f)):
                slurm_script += "%s "%f

            elif (('=' not in f) and ('/' in f)):
                slurm_script += "%s/user_files/%s "%(pwd,os.path.basename(f))
            else:
                argument, fname = f.split('=') 
                if ((fname.isdigit()) or ('/' not in fname)):
                    slurm_script += "%s %s "%(argument,fname)
                    
                elif '=' in f:
                    slurm_script += "%s %s/user_files/%s "%(argument,pwd,os.path.basename(fname))

        if self.output_file is not None:
            for f in self.output_file:
                argument, fname = f.split('=') 
                slurm_script += "%s %s/Output/%s "%(argument,pwd,os.path.basename(fname))

        slurm_script += "\n"
            
        return slurm_script

    #--------------------------------------------------------------------------------------------------
    """
    Load all the configurations specific to the resource defined by user
    """
    def loadConfig(self):
        home = expanduser("~")
        self.home = '%s/Standalone'%home
        try:
            with open('%s/configs/machine_config.json'%LOCAL_HOME) as data_file:
                config = json.load(data_file)

            Kconfig = imp.load_source('Kconfig','./configs/%s.wcfg'%self.kernel_name)
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
            #self.module_test_file = Kconfig.module_test_file
            self.output_file = Kconfig.output_file
            #self.param = Kconfig.param
            #self.module_stage_cmd = Kconfig.stage_module_load
        except Exception:
            print 'error'
            raise


    #---------------------------------------------------------------------------------------------------------
    def job_submit(self):
        #Submit job
        print(Fore.GREEN+"Submitting slurm job"+Fore.RESET)
        p = subprocess.Popen(['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'sbatch %s/Standalone/slurm_script.slurm'%self.wdir],
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
            print(Fore.GREEN+"Submission successful: Job id = "+self.job_id+Fore.RESET)
        else:
            print(Fore.RED+"Submission failure"+Fore.RESET)
            sys.exit(1)


    #--------------------------------------------------------------------------------------------------------------
    def job_check(self):
        #Check for job completion
        command = ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'squeue --job', self.job_id]
        state = None
        print(Fore.GREEN+"Waiting for code to execute..."+Fore.RESET)
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
        print(Fore.GREEN+"Execution complete..."+Fore.RESET)
        print "--------> %s <---------"%state


    #---------------------------------------------------------------------------------------------------------------
    def error_check(self):
        if(self.kernel_name == "amber" or self.kernel_name == "coco" or self.kernel_name == "lsdmap"):
            print(Fore.GREEN+"checking error in "+self.kernel_name+Fore.RESET)
            p = subprocess.Popen(['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'cat %s/Standalone/Output/STDERR'%self.wdir],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            #exitcode = 0
            
            for line in stdout.split("\n"):
                if (("error" in line) or ("Error" in line)):
                    self.exitcode = 1
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
                    elif "ExitCode=0" in line:
                        self.exitcode = 0


    #------------------------------------------------------------------------------------------------------------------
    def cleanup(self):
        #Transfer files from remote to local machine
        files = glob.glob('%s/Output/*'%LOCAL_HOME)
        for f in files:
            os.remove(f)

        print "Transfer output to local machine"
        p = subprocess.Popen(['scp', '-r', '%s@stampede.tacc.utexas.edu:/%s/Standalone/Output/'%(self.uname,self.wdir), '%s/'%LOCAL_HOME ],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        for line in stderr.split("\n"):
            if line is "":
                print "Transfer to local machine successful"
            else:
                print "Transfer Failed"

        #-----------------------------------------------------------------------------------------------------------
        #Clean up remote machine
        command =  ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'chmod', '-R','a+rX','%s/Standalone/'%self.wdir]
        p = subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        
        command =  ['ssh','%s@stampede.tacc.utexas.edu'%self.uname,'rm', '-r','%s/Standalone/'%self.wdir]
        p = subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print(Fore.GREEN+"Removed all the files from remote machine"+Fore.RESET)


    #--------------------------------------------------------------------------------------------------------
    def run(self):
        #-------------------------------------------------------------------------------------------------------
        #Module test
        print(Fore.GREEN+"******************************************"+Fore.RESET)
        print(Fore.GREEN+"*            Module Test: "+self.kernel_name+"        *"+Fore.RESET)
        print(Fore.GREEN+"******************************************"+Fore.RESET)
        slurm_script = self.generateSlurm(self.inp_file)
#        print self.user_modules
        if self.user_modules is None:
            print(Fore.YELLOW+"No user modules found! Using default modules"+Fore.RESET)
            self.copyFilesToRemote(self.inp_file,0,self.pre_exec)
        else:
            print(Fore.YELLOW+"Using user modules")
            self.copyFilesToRemote(self.inp_file,0,self.user_modules)

##        #---------------------------------------------------------------------------------------------------------
        print(Fore.GREEN+"\n******************************************"+Fore.RESET)
        print(Fore.GREEN+"*            Execution Test: "+self.kernel_name+"     *"+Fore.RESET)
        print(Fore.GREEN+"******************************************"+Fore.RESET)
        slurm_script = self.generateSlurm(self.inp_file)
       
        target = open('slurm_script.slurm','w')
        target.write(slurm_script)
        target.close()

        self.copyFilesToRemote(self.inp_file,1,"")
        self.job_submit()
        self.job_check()
        self.error_check()
        self.cleanup()
        if(self.exitcode == 1):
            print(Fore.RED+"Execution failed, Check STDERR file"+Fore.RESET)
            sys.exit(1)
        else:
            print(Fore.GREEN+"The execution is successful, Check Output folder for output. All set to use EnsembleMD"+Fore.RESET)
            
