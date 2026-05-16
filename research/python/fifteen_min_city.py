from __future__ import annotations

from fmc_core import build_arg_parser, run
from fmc_dijkstra_bucket import solve_bucket
from fmc_dijkstra import solve_modified, solve_regular


_SOLVERS = {
    "modified":       solve_modified,
    "regular":        solve_regular,
    "bucket": solve_bucket,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    parser.add_argument(
        "-a", "--algorithm",
        choices=list(_SOLVERS),
        default="modified",
        help="Which shortest-path variant to run (default: modified).",
    )
    args = parser.parse_args(argv)
    return run(
        args,
        algorithm=args.algorithm,
        solver=_SOLVERS[args.algorithm],
    )


if __name__ == "__main__":
    raise SystemExit(main())
