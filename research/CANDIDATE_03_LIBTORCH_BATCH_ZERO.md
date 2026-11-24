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

Research Actions model `candidate_03_libtorch_batch_zero.py` reproduces the zero
divisor as RED and verifies the minimal guard as GREEN. Native libtorch execution is
still required for staging because the module is optional at build time.

## Actual consequence

The trainer can abort with an integer divide-by-zero (or platform-specific undefined
behavior) before training starts for a valid input. This blocks production workflows,
and on platforms where the fault is not trapped can produce invalid batch arithmetic.

## Minimal fix / regression

If `sample_per_batch_1 <= 1`, skip the “one fewer sample per batch” comparison and
return `sample_per_batch_1`; add a regression for `(3,2)` plus existing divisible and
`num_samples < num_batches` cases.

## Collision status

No exact upstream issue/PR collision was found by source-symbol and parameter searches
at `next` HEAD `09f3b86652118bc759d889fe0235434c4bb02a54`.

## Gate status

- G01 hypothesis: PASS
- G02 environment: LIMITED until native libtorch GC test
- G03 materiality: production startup failure for valid small datasets
- G04 collision: no exact collision found
- G05 evidence: deterministic model + source contract
- G06: GO to native GC validation
