import argparse
from handler import Handler
from helpers import Colour

parser = argparse.ArgumentParser()
parser.add_argument("--colour", type=str, choices=["w", "b"], default="w", help="choose your colour (default white)")
parser.add_argument("--fen", type=str, default="startpos", help="pass fen string to start from a specific position (default startpos)")
parser.add_argument("--movetime", type=int, default=1000, help="set time the engine spends on each move, in milliseconds (default 1000)")
parser.add_argument('--verbose', type=int, choices=[0, 1], default=0, help="Set verbosity of logs (default 0)")

args = parser.parse_args()
verbose = args.verbose
movetime = args.movetime
fen = args.fen

colour = Colour.WHITE if args.colour == "w" else Colour.BLACK
engine_colour = colour.flipped()
handler = Handler(verbose=verbose, movetime=movetime, engine_color=engine_colour, fen=fen)
handler.run()
