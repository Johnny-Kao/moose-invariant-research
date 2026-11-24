#!/usr/bin/env python3
"""Deterministic model of BayesianActiveLearner convergence filtering."""

import math


def production_convergence(log_likelihood, current):
    value = 0.0
    num_valid = 0
    for lhs, rhs in zip(log_likelihood, current):
        if not math.isnan(lhs):
            value += (lhs - rhs) ** 2
            num_valid += 1
    return math.sqrt(value) / num_valid


def fixed_convergence(log_likelihood, current):
    value = 0.0
    num_valid = 0
    for lhs, rhs in zip(log_likelihood, current):
        if not math.isnan(lhs):
            value += (lhs - rhs) ** 2
            num_valid += 1
    if num_valid == 0:
        raise ValueError("Bayesian active learner has no finite likelihood values")
    return math.sqrt(value) / num_valid


def main():
    # Python raises where C++ floating arithmetic yields a NaN; both violate the
    # finite convergence invariant.
    try:
        production_convergence([math.nan, math.nan], [1.0, 2.0])
    except ZeroDivisionError:
        print("RED: all-NaN likelihood set divides convergence by zero")
    else:
        raise AssertionError("production model unexpectedly accepted no valid values")
    try:
        fixed_convergence([math.nan, math.nan], [1.0, 2.0])
    except ValueError as exc:
        print("GREEN: explicit no-valid-likelihood diagnostic:", exc)
    else:
        raise AssertionError("fixed model must reject an empty finite set")


if __name__ == "__main__":
    main()
