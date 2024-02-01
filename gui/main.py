import argparse
from handler import Handler
from helpers import Colour

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', type=int, choices=[0, 1], default=0, help='Set verbosity of logs (0 or 1)')
parser.add_argument("--movetime", type=int, default=1000, help="Set movetime in ms (default 1000)")
parser.add_argument("--colour", type=str, choices=["w", "b"], default="w", help="choose your colour (w/b)")
parser.add_argument("--fen", type=str, default="startpos", help="Start from a given FEN (default is starting position)")

args = parser.parse_args()
verbose = args.verbose
movetime = args.movetime
fen = args.fen

colour = Colour.WHITE if args.colour == "w" else Colour.BLACK
engine_colour = colour.flipped()
handler = Handler(verbose=verbose, movetime=movetime, engine_color=engine_colour, fen=fen)
handler.run()
