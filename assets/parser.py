import discord
import argparse, shlex

class Arguments(argparse.ArgumentParser):
	def error(self, message):
		raise RuntimeError(message)

def parse_arguments(ctx, args=None):
    parser = Arguments(add_help=False, allow_abbrev=False)
    parser.add_argument("--flag", nargs="+")
    
    args = parser.parse_args(shlex.split(args))
    return args.flag[0]