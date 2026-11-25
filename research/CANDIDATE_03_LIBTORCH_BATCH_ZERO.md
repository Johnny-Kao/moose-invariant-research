# Candidate 03 — zero divisor in libtorch ANN batch-size selection

## Hypothesis

`LibtorchArtificialNeuralNetTrainer::computeBatchSize()` computes
`sample_per_batch_2 = sample_per_batch_1 - 1`, then divides by it. For the valid
configuration `(num_samples, num_batches) = (3, 2)`, `sample_per_batch_1 == 1`
and the divisor is zero.

## Production reachability

`LibtorchANNTrainer` exposes `num_batches` with only the contract `1<=num_batches`.
Three collected samples and two requested batches are ordinary small-data training,
and no caller-side guard excludes this case.

## Violated invariant

Batch-size selection must return a finite positive batch size for every valid input;
the comparison branch must never construct a zero divisor.

## Reproduction result

Research Actions model plus a C++ UBSan harness reproduce the zero divisor as RED
and verify the minimal guard as GREEN: [45470911015](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45470911015).
The native MOOSE training entry point independently reproduces the failure with the
official C++ libtorch package: [45590977786](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45590977786).
The runner reports `Floating point exception` for the unchanged valid input. After
the one-line guard, the same native command completes successfully:
[45598038583](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45598038583).

## Actual consequence

The trainer can abort with an integer divide-by-zero (or platform-specific undefined
behavior) before training starts for a valid input. This blocks production workflows,
and on platforms where the fault is not trapped can produce invalid batch arithmetic.

## Minimal fix / regression

If `sample_per_batch_1 <= 1`, skip the “one fewer sample per batch” comparison and
return `sample_per_batch_1`; the native workflow is the regression for `(3,2)` plus
the existing test object's normal setup.

## Collision status

No exact upstream issue/PR collision was found by source-symbol and parameter searches
at `next` HEAD `a75b6945b77ef4d783406982cea3e9ff753903a0`.

## Gate status

- G01 hypothesis: PASS
- G02 environment: PASS (official C++ libtorch on GC)
- G03 materiality: production startup failure for valid small datasets
- G04 collision: no exact collision found
- G05 evidence: native RED and native GREEN
- G06: GO for maintainer review; no upstream issue/PR opened yet
