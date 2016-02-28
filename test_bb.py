
from blackbox import Blackbox


if __name__ == "__main__":
    test = Blackbox(name = 'coco',
                    resource = 'xsede.stampede',
                    )
    test.run()
    #test.dispFile()
