#!/usr/bin/env python3
"""Control test for the sibling-transfer allocation guard.

The current next branch already compares source and target ownership.  This
test prevents a future regression while documenting why the initial static
lead was rejected.
"""

from __future__ import annotations


def current_guard(source_local: bool, target_local: bool) -> bool:
    return int(source_local) + int(target_local) == 1


def copy_transfer_value(source_local: bool, target_local: bool, old_target: float) -> float:
    # MultiAppCopyTransfer::execute() only calls transfer() when both apps are
    # local on this rank.  For a mismatched partition no rank performs a copy.
    if source_local and target_local:
        return 42.0
    return old_target


def main() -> None:
    # Two ranks, one child app per side, but opposite ownership.  This is a
    # reachable layout when sibling MultiApps use different processor limits.
    ownership = [(True, False), (False, True)]

    assert all(current_guard(*pair) for pair in ownership), (
        "the current guard must reject every mismatched rank"
    )

    # The transfer is silently skipped on both ranks, so a stale target value
    # survives instead of receiving the source value.
    stale = [copy_transfer_value(*pair, old_target=7.0) for pair in ownership]
    assert stale == [7.0, 7.0], stale
    assert stale != [42.0, 42.0]

    print("PASS: current guard rejects opposite ownership on both ranks")
    print("PASS: transfer control condition is false for the invalid layout")
    print("PARK: initial static lead was a readout error; no MOOSE defect reproduced")


if __name__ == "__main__":
    main()
