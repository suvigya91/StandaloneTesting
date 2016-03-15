
from blackbox import Standalone


if __name__ == "__main__":
    test = Standalone(name = 'lsdmap',
                    resource = 'xsede.stampede',
##                    inp_files = ['-i=/home/suvigya/inp/min.in',
##                                 '-p=/home/suvigya/inp/penta.top',
##                                 '-c=/home/suvigya/inp/penta.crd',
##                                 '-inf=/home/suvigya/inp/min.inf',
##                                 '-r=/home/suvigya/inp/md.crd',
##                                 '-ref=/home/suvigya/inp/min.crd']
##                      inp_files = ['--topfile=/home/suvigya/inp/penta.top',
##                                   '--mdfile=/home/suvigya/inp/*.ncdf']
##                      inp_files = ['runfile=/home/suvigya/inp/run.py',
##                                   'mdpfile=/home/suvigya/inp/grompp.mdp',
##                                   'startfile=/home/suvigya/inp/start.gro',
##                                   'topfile=/home/suvigya/inp/topol.top']
                      inp_files = ['-f=/home/suvigya/inp/config.ini',
                                   '-w=/home/suvigya/inp/weight.w',
                                   '-c=/home/suvigya/inp/tmp.gro',
                                   '-n=/home/suvigya/inp/out.nn']
                    )
    test.run()
    #test.dispFile()
