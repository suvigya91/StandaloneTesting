#Example code

from j_blackbox import Standalone


if __name__ == "__main__":
    test = Standalone(name = 'lsdmap',
                    resource = 'xsede.stampede',
##                    inp_files = ['mininfile=/home/suvigya/inp/min.in',
##                                 'topfile=/home/suvigya/inp/penta.top',
##                                 'crdfile=/home/suvigya/inp/penta.crd',
##                                 'nwinfo=/home/suvigya/inp/min.inf',
##                                 'nwcoords=/home/suvigya/inp/md.crd',
##                                 'refcoords=/home/suvigya/inp/min.crd']
##                      inp_files = ['topfile=/home/suvigya/inp/penta.top',
##                                   'mdfile=/home/suvigya/inp/*.ncdf']
##                      inp_files = ['runfile=/home/suvigya/inp/run.py',
##                                   'mdpfile=/home/suvigya/inp/grompp.mdp',
##                                   'startfile=/home/suvigya/inp/start.gro',
##                                   'topfile=/home/suvigya/inp/topol.top']
                      inp_files = ['configfile=/home/suvigya/inp/config.ini',
                                   'weightfile=/home/suvigya/inp/weight.w',
                                   'structfile=/home/suvigya/inp/tmp.gro',
                                   'nnfile=/home/suvigya/inp/out.nn']
                    )
    test.run()
    #test.dispFile()
