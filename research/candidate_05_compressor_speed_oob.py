#!/usr/bin/env python3
"""Deterministic bounds model for compressor speed interpolation."""


def production_indices(speeds, speed):
    if speed == speeds[0]:
        return 0, 0
    if speed < speeds[0]:
        return 0, 1
    if speed > speeds[-1]:
        return len(speeds) - 1, len(speeds) - 2
    # Mirrors lower_bound/upper_bound interpolation index arithmetic.
    x1 = next(i for i, value in enumerate(speeds) if value >= speed) - 1
    x2 = next(i for i, value in enumerate(speeds) if value > speed)
    return x1, x2


def main():
    # The parameter contract checks only equal vector lengths, so one speed and
    # one function are accepted. A runtime speed above the sole table point
    # reaches the extrapolation branch and indexes x2 = -1; a speed below it
    # indexes x2 = 1. Both violate the intended two-point interpolation contract.
    x1, x2 = production_indices([1.0], 0.5)
    assert (x1, x2) == (0, 1)
    print("RED: one speed point yields out-of-bounds interpolation index", (x1, x2))

    if len([1.0]) < 2:
        raise ValueError("compressor speed tables require at least two points")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print("GREEN: minimal cardinality guard rejects the unsafe table:", exc)
