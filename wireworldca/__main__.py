from dataclasses import dataclass
from argparse import ArgumentParser, Namespace
import os
import sys

from tqdm import tqdm

from wireworldca.ca import set_seed, run_experiment

__TITLE__ = "Wireworld Half-Adder Experiments"

@dataclass
class WireworldArgs:
    num_tests: int
    grid_size: list[int]
    num_adders: int
    max_steps: int
    output_dir: str
    seed: int

    @classmethod
    def constructor(cls, args: Namespace):
        if not all([*dict(args._get_kwargs()).values(), *args._get_args()]):
            raise ValueError("Missing one or more required arguments")
        if not 0 < args.seed < 2**32 - 1:
            raise ValueError("Provided seed must be between 1 and 2³² - 1")
        os.makedirs(args.output_dir, exist_ok=True)
        if not os.path.isdir(args.output_dir):
            raise ValueError(f"Invalid output path provided: {repr(args.output_dir)}")
        return cls(
            num_tests = int(args.num_tests),
            grid_size = list(args.grid_size),
            num_adders = int(args.num_adders),
            max_steps = int(args.max_steps),
            output_dir = args.output_dir,
            seed = int(args.seed)
        )

    @classmethod
    def parse(cls) -> 'Args':
        parser = ArgumentParser(description=f"Run {__TITLE__}")
        parser.add_argument("--num_tests", type=int, default=10, help="Number of experiments to run (Default: 10)")
        parser.add_argument("--grid_size", type=int, nargs=2, default=[128, 128], help="Grid size (rows, cols) (Default: 128, 128)")
        parser.add_argument("--num_adders", type=int, default=10, help="Number of Half-Adders per test (Default: 10)")
        parser.add_argument("--max_steps", type=int, default=150, help="Maximum simulation steps per test (Default: 150)")
        parser.add_argument("--output_dir", type=str, default="./wwca_experiment", help="Output directory (Default: ./wwca_experiment)")
        parser.add_argument("--seed", type=int, default=13374269, help="PRNG seed (for repeatability) (Default: 13374269)")
        return cls.constructor(parser.parse_args())

def main():
    args = WireworldArgs.parse()

    set_seed(args.seed)

    for test_num in range(args.num_tests):
        run_experiment(test_num, tuple(args.grid_size), args.num_adders, args.max_steps, args.output_dir, test_num+1)

if __name__ == "__main__":
    main()
