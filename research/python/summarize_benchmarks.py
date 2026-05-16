from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Iterable

from fmc_core import GRAPHS, GRAPHS_DIR


ALGORITHMS: tuple[str, ...] = ("modified", "regular", "bucket")
MODES: tuple[str, ...] = ("sequential", "parallel")


def _result_path(graph: str, algorithm: str, mode: str) -> Path:
    suffix = "_parallel" if mode == "parallel" else ""
    return GRAPHS_DIR / f"{graph}_15mc_{algorithm}{suffix}.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _fmt_seconds(value: float) -> str:
    return f"{value:9.6f}"


def _summary_row(runs: list[float]) -> tuple[float, float, float, float]:
    mean = statistics.mean(runs)
    stdev = statistics.stdev(runs) if len(runs) > 1 else 0.0
    return mean, stdev, min(runs), max(runs)


def _print_timing_table(records: dict[tuple[str, str, str], dict]) -> None:
    header = (
        f"{'graph':<17} {'algorithm':<10} {'mode':<11} "
        f"{'runs':>4} {'mean [s]':>10} {'stdev [s]':>10} "
        f"{'min [s]':>10} {'max [s]':>10}"
    )
    print(header)
    print("-" * len(header))
    for graph in GRAPHS:
        for algorithm in ALGORITHMS:
            for mode in MODES:
                key = (graph, algorithm, mode)
                rec = records.get(key)
                if rec is None:
                    print(
                        f"{graph:<17} {algorithm:<10} {mode:<11} "
                        f"{'-':>4} {'(missing)':>10}"
                    )
                    continue
                runs = rec["runs_seconds"]
                mean, stdev, mn, mx = _summary_row(runs)
                print(
                    f"{graph:<17} {algorithm:<10} {mode:<11} "
                    f"{len(runs):>4} "
                    f"{_fmt_seconds(mean):>10} {_fmt_seconds(stdev):>10} "
                    f"{_fmt_seconds(mn):>10} {_fmt_seconds(mx):>10}"
                )
        print()


def _node_lists_equal(
    label_a: str, list_a: list, label_b: str, list_b: list,
) -> tuple[bool, str]:
    if list_a == list_b:
        return True, f"OK ({len(list_a)} nodes)"
    set_a, set_b = set(list_a), set(list_b)
    only_a = set_a - set_b
    only_b = set_b - set_a
    return False, (
        f"MISMATCH: |{label_a}|={len(list_a)} vs |{label_b}|={len(list_b)}; "
        f"only in {label_a}: {len(only_a)}, only in {label_b}: {len(only_b)}"
    )


def _check_intersection_and_categories(
    rec_a: dict, label_a: str, rec_b: dict, label_b: str,
) -> tuple[bool, list[str]]:
    messages: list[str] = []
    ok_all = True

    ok, msg = _node_lists_equal(
        f"{label_a}.intersection", rec_a["intersection"],
        f"{label_b}.intersection", rec_b["intersection"],
    )
    messages.append(f"  intersection: {msg}")
    ok_all &= ok

    cats_a = set(rec_a["per_category"])
    cats_b = set(rec_b["per_category"])
    if cats_a != cats_b:
        messages.append(
            f"  per_category keys differ: only in {label_a}: "
            f"{sorted(cats_a - cats_b)}, only in {label_b}: "
            f"{sorted(cats_b - cats_a)}"
        )
        return False, messages

    for cat in sorted(cats_a):
        ok, msg = _node_lists_equal(
            f"{label_a}.{cat}", rec_a["per_category"][cat],
            f"{label_b}.{cat}", rec_b["per_category"][cat],
        )
        messages.append(f"  per_category[{cat}]: {msg}")
        ok_all &= ok

    return ok_all, messages


def _check_metadata_consistent(
    pair_label: str, rec_a: dict, rec_b: dict, fields: Iterable[str],
) -> list[str]:
    out: list[str] = []
    for field in fields:
        if rec_a.get(field) != rec_b.get(field):
            out.append(
                f"  [WARN] {pair_label}: {field} differs "
                f"({rec_a.get(field)!r} vs {rec_b.get(field)!r})"
            )
    return out


def _cross_variant_checks(
    records: dict[tuple[str, str, str], dict],
) -> bool:
    all_ok = True
    print("== Cross-variant correctness (modified vs regular vs bucket) ==")
    for graph in GRAPHS:
        for mode in MODES:
            present = [
                a for a in ALGORITHMS if (graph, a, mode) in records
            ]
            if len(present) < 2:
                print(
                    f"[{graph}, {mode}] only {len(present)} variant(s) "
                    f"available ({present}); skipping."
                )
                continue
            base_algo = present[0]
            base = records[(graph, base_algo, mode)]
            for other_algo in present[1:]:
                other = records[(graph, other_algo, mode)]
                pair_label = (
                    f"{graph}/{mode}: {base_algo} vs {other_algo}"
                )
                print(f"[{pair_label}]")
                meta = _check_metadata_consistent(
                    pair_label, base, other,
                    fields=("graph", "threshold_minutes", "n_nodes", "n_edges"),
                )
                for line in meta:
                    print(line)
                ok, messages = _check_intersection_and_categories(
                    base, base_algo, other, other_algo,
                )
                for line in messages:
                    print(line)
                all_ok &= ok
            print()
    return all_ok


def _mode_consistency_checks(
    records: dict[tuple[str, str, str], dict],
) -> bool:
    all_ok = True
    print("== Mode consistency (sequential vs parallel) ==")
    for graph in GRAPHS:
        for algorithm in ALGORITHMS:
            seq_key = (graph, algorithm, "sequential")
            par_key = (graph, algorithm, "parallel")
            if seq_key not in records or par_key not in records:
                missing = [
                    m for m, k in (("sequential", seq_key), ("parallel", par_key))
                    if k not in records
                ]
                print(
                    f"[{graph}/{algorithm}] missing: {missing}; skipping."
                )
                continue
            seq = records[seq_key]
            par = records[par_key]
            pair_label = f"{graph}/{algorithm}: sequential vs parallel"
            print(f"[{pair_label}]")
            meta = _check_metadata_consistent(
                pair_label, seq, par,
                fields=("graph", "threshold_minutes", "n_nodes", "n_edges"),
            )
            for line in meta:
                print(line)
            ok, messages = _check_intersection_and_categories(
                seq, "sequential", par, "parallel",
            )
            for line in messages:
                print(line)
            all_ok &= ok
        print()
    return all_ok


def _load_all() -> dict[tuple[str, str, str], dict]:
    records: dict[tuple[str, str, str], dict] = {}
    for graph in GRAPHS:
        for algorithm in ALGORITHMS:
            for mode in MODES:
                path = _result_path(graph, algorithm, mode)
                if not path.is_file():
                    continue
                records[(graph, algorithm, mode)] = _load(path)
    return records


def main() -> int:
    records = _load_all()
    if not records:
        print(
            f"No benchmark JSONs found under {GRAPHS_DIR}. "
            f"Run fifteen_min_city.py first."
        )
        return 1

    print("== Timing summary (per-iteration wall-clock) ==")
    _print_timing_table(records)

    cross_ok = _cross_variant_checks(records)
    mode_ok = _mode_consistency_checks(records)

    if cross_ok and mode_ok:
        print("All correctness checks passed.")
        return 0
    print("Some correctness checks FAILED. See diagnostics above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
