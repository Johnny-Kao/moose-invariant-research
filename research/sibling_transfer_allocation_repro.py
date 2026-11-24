#!/usr/bin/env python3
"""Deterministic reproducer for the sibling-transfer allocation guard.

This models the exact boolean guard and the exact MultiAppCopyTransfer sibling
execution condition.  It deliberately does not claim to be a full MOOSE run;
it is a cheap contract-level RED/GREEN test that can run before a MOOSE build.
"""

from __future__ import annotations


def buggy_guard(source_local: bool, target_local: bool) -> bool:
    # Current next branch in five sibling-transfer validators.  The second
    # operand should be target_local, but repeats source_local.
    return int(source_local) + int(source_local) == 1


def fixed_guard(source_local: bool, target_local: bool) -> bool:
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

    assert all(not buggy_guard(*pair) for pair in ownership), (
        "the current guard unexpectedly detected the mismatched partition"
    )
    assert all(fixed_guard(*pair) for pair in ownership), (
        "the minimal guard must reject every mismatched rank"
    )

    # The transfer is silently skipped on both ranks, so a stale target value
    # survives instead of receiving the source value.
    stale = [copy_transfer_value(*pair, old_target=7.0) for pair in ownership]
    assert stale == [7.0, 7.0], stale
    assert stale != [42.0, 42.0]

    print("RED: buggy guard accepts opposite ownership on both ranks")
    print("RED: sibling copy executes on zero ranks; target remains stale [7.0, 7.0]")
    print("GREEN: replacing second source hasLocalApp() with target hasLocalApp() rejects both ranks")


if __name__ == "__main__":
    main()
