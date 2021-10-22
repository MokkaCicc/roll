from argparse import ArgumentParser, Namespace
from typing import Match
from random import randint
import re

NAME = "roll"
VERSION = "1.0.0"

RE_DICE = re.compile(r'(?P<dices>[\d]*)d(?P<faces>[\d]+)(?P<mod>[+-][\d]+)?')
RE_FUDGE = re.compile(r'(?P<dices>[\d]*)f(?P<mod>[+-][\d]+)?')
DICES_DEFAULT = 1
MOD_DEFAULT = 0
DICES_MAX = 1000
FACES_MAX = 1000000
MOD_MAX = 1000000


def init_parser()->ArgumentParser:
	parser = ArgumentParser(
		prog=NAME,
		description="Roll some dices",
		epilog="Let's roll! 🎲",
		allow_abbrev=False
	)
	parser.add_argument(
		"-v", "--version", action='version',
		version=f"{NAME} {VERSION}"
	)
	parser.add_argument(
		"formula", action='store',
		metavar='formula', type=str,
		help="The dice formula"
	)
	total_mod = parser.add_mutually_exclusive_group(required=False)
	total_mod.add_argument(
		"-L", "--lower", action='store_true',
		dest='lower',
		help="Return the lower dice instead of the total"
	)
	total_mod.add_argument(
		"-H", "--highest", action='store_true',
		dest='highest',
		help="Return the highest dice instead of the total"
	)
	total_mod.add_argument(
		"-m", "--mean", action='store_true',
		dest='mean',
		help="Return the mean value"
	)
	parser.add_argument(
		"-s", "--sorted", action='store_true',
		dest='sorted',
		help="Return the results sorted"
	)
	return parser


def parse_dice(match:Match)->tuple[int, int, int]:
	dices = DICES_DEFAULT if not match.group('dices') else int(match.group('dices'))
	faces = int(match.group('faces'))
	mod = MOD_DEFAULT if not match.group('mod') else int(match.group('mod'))
	if dices > DICES_MAX or faces > FACES_MAX or mod > MOD_MAX:
		raise SystemExit(f"{NAME}: error: argument number: number too big")
	return dices, faces, mod

def parse_fudge(match:Match)->tuple[int, int]:
	dices = DICES_DEFAULT if not match.group('dices') else int(match.group('dices'))
	mod = MOD_DEFAULT if not match.group('mod') else int(match.group('mod'))
	if dices > DICES_MAX or mod > MOD_MAX:
		raise SystemExit(f"{NAME}: error: argument number: number too big")
	return dices, mod

# need some refacto
def parse_args(total:int, results:list[int], args:Namespace)->tuple[int, int]:
	sorted_results = list(results)
	sorted_results.sort()
	if args.lower or args.highest:
		new_total = sorted_results[0] if args.lower else sorted_results[-1]
		new_results = sorted_results if args.sorted else results
		return new_total, new_results
	if args.mean:
		mean = round(total/len(results))
		new_results = sorted_results if args.sorted else results
		return mean, new_results
	if args.sorted:
		return total, sorted_results
	return total, results

def print_results(formula:str, total:int, results:list[int])->None:
	print(f"{formula}: {total} -> {results}")


def throw_dices(dices:int, faces:int)->tuple[int, list[int]]:
	results = list()
	for i in range(dices):
		results.append(throw_dice(faces))
	total = sum(results)
	return total, results

def throw_dice(faces:int)->int:
	return randint(0, faces)


def throw_fudge_dices(dices:int)->tuple[int, list[int]]:
	results = list()
	for i in range(dices):
		results.append(throw_fudge_dice())
	total = sum(results)
	return total, results

def throw_fudge_dice()->int:
	return randint(-1, 1)


def main()->None:
	parser = init_parser()
	args = parser.parse_args()
	formula = args.formula.lower()

	match = re.match(RE_DICE, formula)
	if match and formula == match.group():
		dices, faces, mod = parse_dice(match)
		total, results = throw_dices(dices, faces)
		total, results = parse_args(total, results, args)
		total += mod
		print_results(match.group(), total, results)
		return

	match = re.match(RE_FUDGE, formula)
	if match and formula== match.group():
		dices, mod = parse_fudge(match)
		total, results = throw_fudge_dices(dices)
		total, results = parse_args(total, results, args)
		total += mod
		print_results(match.group(), total, results)
		return

	raise SystemExit(f"{NAME}: error: argument number: invalid dice formula: '{args.formula}'")


if __name__ == '__main__':
	main()
