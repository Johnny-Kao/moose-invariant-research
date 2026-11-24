# Candidate 04 — Bayesian active learner divides by zero after all likelihoods are NaN

## Hypothesis

`BayesianActiveLearner::computeConvergenceValue()` filters non-finite likelihoods
with `!std::isnan`, increments `num_valid`, and unconditionally computes
`sqrt(convergence_value) / num_valid`. If every likelihood is NaN, `num_valid` is
zero.

## Production reachability

Likelihood values come from user-configured likelihood functions and GP evaluation.
An invalid proposal, failed/underflowed likelihood, or non-finite variance can make
all entries NaN; there is no precondition requiring one finite value. The method is
called by `GenericActiveLearnerTempl::execute()` to update the convergence state.

## Violated invariant

The convergence metric must be finite or fail explicitly; an empty finite sample set
must never be represented by an arithmetic NaN.

## Reproduction result

Research Actions model `candidate_04_bayesian_active_nan.py` reproduces the zero-valid
path as RED and verifies an explicit diagnostic as GREEN. Native libtorch integration
is still required before staging. A follow-up Linux C++ NaN-state harness passed in
[45471574817](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45471574817).

## Actual consequence

The active-learning controller receives NaN instead of a convergence metric. Depending
on the configured comparison, this can suppress stopping or make the loop continue
with invalid acquisition inputs rather than reporting the failed likelihood evaluation.

## Minimal fix / regression

Check `num_valid == 0` and issue a targeted `mooseError` (or documented retry state)
before division. Add a regression with all-NaN likelihoods and a mixed finite/NaN case
that preserves the existing metric.

## Collision status

No exact upstream issue/PR collision was found for `computeConvergenceValue` or
`num_valid` at `next` HEAD `a75b6945b77ef4d783406982cea3e9ff753903a0`.

## Gate status

- G01 hypothesis: PASS
- G02 environment: LIMITED until native libtorch GC test
- G03 materiality: silent NaN convergence state in an adaptive controller
- G04 collision: no exact collision found
- G05 evidence: deterministic model + source contract
- G06: GO to native GC validation
