import argparse
from handler import Handler
from helpers import Colour

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', type=int, choices=[0, 1], default=0, help='Set verbosity level (0 or 1)')
parser.add_argument("--movetime", type=int, default=1000, help="Set movetime in ms (default 1000)")
parser.add_argument("--color", type=str, choices=["w", "b"], help="Set color (w or b)", required=True)
parser.add_argument("--fen", type=str, default="startpos", help="Start from a given FEN (default is starting position)")
args = parser.parse_args()
verbose = args.verbose
movetime = args.movetime
color = Colour.WHITE if args.color == "w" else Colour.BLACK
engine_color = color.flipped()
fen = args.fen
handler = Handler(verbose=verbose, movetime=movetime, engine_color=engine_color, fen=fen)
handler.run()
