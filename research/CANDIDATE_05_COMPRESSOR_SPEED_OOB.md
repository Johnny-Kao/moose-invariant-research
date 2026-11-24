# Candidate 05 — compressor speed table can index past a one-point table

## Hypothesis

`ADShaftConnectedCompressor1PhaseUserObject` validates only that `speeds`,
`Rp_functions`, and `eff_functions` have equal lengths. It does not require at
least two speed points. In `computeFluxesAndResiduals()`, any non-exact speed
with a one-point table selects interpolation/extrapolation indices that include
index 1 or -1, then dereferences all three vectors.

## Production reachability

One speed curve is accepted by the current parameter contract. A compressor can
operate at a speed different from that table point during startup, shutdown, or
control changes, reaching the unsafe branch.

## Violated invariant

The interpolation path requires two distinct bracketing/extrapolation points;
vector accesses must be in bounds before evaluating pressure-ratio and efficiency
functions.

## Reproduction result

Research Actions model plus a C++ ASan harness reproduce the one-point table index
`(0,1)` as RED and verify a minimum-cardinality guard as GREEN:
[45470918068](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45470918068).
Native thermal-hydraulics integration is still required before staging.

## Actual consequence

The path can read beyond `_speeds`, `_Rp_functions`, and `_eff_functions`, causing
undefined behavior or silently using unrelated memory in a production compressor
simulation.

## Minimal fix / regression

Require at least two speed/function entries in `validParams()` and add a failure
regression for one-point tables plus a normal two-point interpolation test. If a
single-point constant curve is intended, implement an explicit constant branch
instead of entering interpolation.

## Collision status

No exact issue/PR collision was found for the class, speed-table cardinality, or
the index logic at `next` HEAD `09f3b86652118bc759d889fe0235434c4bb02a54`.

## Gate status

- G01 hypothesis: PASS
- G02 environment: LIMITED until native thermal-hydraulics GC test
- G03 materiality: memory safety / wrong compressor map values
- G04 collision: no exact collision found
- G05 evidence: deterministic bounds model + source contract
- G06: GO to native GC validation
