"""
# This is the testing ground.
# Develop functions here, but do not leave them here!
# This is a glorified playground to make a mess in!
"""

import Listener as l
import time as t


def main():
    listener = l.ListenerObj()
    listener.should_listen = True
    listener.checkListenerStatus()
    while listener.selector_id < 10:
        t.sleep(0.5)
        print('num_selecta: ' + str(listener.selector_id))
        listener.checkListenerStatus()
    listener.stopListener()



if __name__ == '__main__':
    main()
