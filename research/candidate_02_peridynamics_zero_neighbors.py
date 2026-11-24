#!/usr/bin/env python3
"""Deterministic model for PeridynamicsMesh isolated-element spacing."""

import math


def production_spacing(dist_sum, neighbor_count):
    # Mirrors: dist_sum / n_fe_neighbors in PeridynamicsMesh.C.
    return dist_sum / neighbor_count


def fixed_spacing(dist_sum, neighbor_count, fallback):
    # Minimal-fix policy: an isolated material point has no neighbor-derived
    # spacing; reject it explicitly instead of publishing NaN/Inf downstream.
    if neighbor_count == 0:
        raise ValueError("isolated peridynamic point has no neighbor spacing")
    return dist_sum / neighbor_count


def main():
    # A valid FE block selection can contain one converted element. The loop in
    # PeridynamicsMesh then observes no face neighbors.
    try:
        value = production_spacing(0.0, 0)
    except ZeroDivisionError:
        value = math.nan
    assert math.isnan(value)
    print("RED: isolated converted element publishes undefined average spacing")

    try:
        fixed_spacing(0.0, 0, fallback=1.0)
    except ValueError as exc:
        print("GREEN: minimal fix rejects undefined spacing before horizon construction:", exc)
    else:
        raise AssertionError("fixed path must not continue with an undefined spacing")


if __name__ == "__main__":
    main()
