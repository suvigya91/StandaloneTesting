#Example code

from j_blackbox import Standalone


if __name__ == "__main__":
    test = Standalone(name = 'coco',
                    resource = 'xsede.stampede',
                      inp_files = ['topfile=/var/lib/jenkins/inp/penta.top',
                                   'mdfile=/var/lib/jenkins/inp/*.ncdf']

                    )
    test.run()
    #test.dispFile()
