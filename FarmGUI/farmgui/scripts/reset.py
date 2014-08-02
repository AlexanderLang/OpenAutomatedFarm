from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys

from ..communication import SerialShell


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <dev_name>\n'
          '(example: "%s /dev/ttyACM0")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    dev_name = argv[1]
    serial = SerialShell(dev_name)
    serial.set_id(0)