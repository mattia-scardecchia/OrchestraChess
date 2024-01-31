import argparse
from handler import Handler


parser = argparse.ArgumentParser()
parser.add_argument('--verbose', type=int, choices=[0, 1], default=0, help='Set verbosity level (0 or 1)')
args = parser.parse_args()
verbose = args.verbose

handler = Handler(verbose=verbose)
handler.run()
