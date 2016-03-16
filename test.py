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

if __name__ == "__main__":
	p = subprocess.Popen(['scp','/home/suvigya/inp/*.ncdf' , 'tg831932@stampede.tacc.utexas.edu:${HOME}/Standalone/user_files'])
                                 #stdin=subprocess.PIPE,
                                 #stdout=subprocess.PIPE,
                                 #stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
