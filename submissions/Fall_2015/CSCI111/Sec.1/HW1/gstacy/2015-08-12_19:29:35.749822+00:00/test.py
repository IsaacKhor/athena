import sys
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('action', choices=['compare', 'collapse', 'filter'])
parser.add_argument('-a', '--annofile')
parser.add_argument('--sorted', action='store_true')
parser.add_argument('--min_reads')
args = vars(parser.parse_args())
print args
