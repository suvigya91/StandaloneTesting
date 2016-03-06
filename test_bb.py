
from blackbox import Standalone


if __name__ == "__main__":
    test = Standalone(name = 'coco',
                    resource = 'xsede.stampede',
##                    inp_files = ['mininfile=/home/suvigya/inp/min.in',
##                                 'topfile=/home/suvigya/inp/penta.top',
##                                 'crdfile=/home/suvigya/inp/penta.crd',
##                                 'nwinfo=/home/suvigya/inp/min.inf',
##                                 'nwcoords=/home/suvigya/inp/md.crd',
##                                 'refcoords=/home/suvigya/inp/min.crd']
                      inp_files = ['topfile=/home/suvigya/inp/penta.top',
                                   'mdfile=/home/suvigya/inp/*.ncdf']
                    )
    test.run()
    #test.dispFile()
