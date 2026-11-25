# Candidate 01 — AMR callback uses an uninitialized transfer grouping

## Hypothesis

`MeshChangedInterface` can call `meshChanged()` during initial AMR before
`initialSetup()` has assigned `_apps_per_component`. The callback enters
`cacheElemToPostprocessorData()` and evaluates `numGlobalApps() /
_apps_per_component`, producing a divide-by-zero before the transfer is ready.
Independently, later cache rebuilds append to `_cached_multiapp_pos_ids` and
`_needed_postprocessors` instead of replacing them.

## Production reachability

The transfer implements `MeshChangedInterface`; `meshChanged()` directly calls
the cache builder after mesh changes. Adaptive mesh refinement/coarsening is a
normal MOOSE execution path. The transfer is used to map sub-application
postprocessors back onto a parent constant-monomial auxiliary variable.

## Violated invariants

1. A mesh-change callback must not use transfer state that `initialSetup()` has
   not initialized.
2. The cache must have exactly one current entry per current active element (and
   component grouping), in the same iteration order used by `execute()`; a
   rebuild must replace, not append to, the previous mapping.

## Reproduction result

The native Linux MOOSE probe first failed on the unmodified path with a real
`Floating point exception` (exit code 136) during the AMR input, while the
existing transfer baseline passed: [RED run
45449298449](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45449298449).
The log shows the failure immediately after the AMR input initializes the
transfer, consistent with division by `_apps_per_component` before setup.
The deterministic lifecycle model also reproduces the later stale-prefix
mapping (`[0, 1, 2]` consumed instead of `[2, 0, 1]`) in
`candidate_01_sample_pp_amr_cache.py`.

The first fixed-source native run removed the FPE and completed the AMR input,
but the harness initially used an invalid zero-error oracle and failed on finite
nonzero values. The corrected harness only requires completion and finite
postprocessor output, and passed on the same native Linux setup:
[GREEN run 45559576212](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45559576212).
The probe reported finite values `[-2.0, 1.8710505174971, 0.0034154370748973,
0.0034154370748973]`; these are observed diagnostics, not an assumed zero-error
oracle.

## Actual consequence

With initial AMR, a production run can abort before advancing the simulation.
With later mesh changes, postprocessor values can be written to the wrong
parent elements or array components, silently corrupting coupled results.

## Minimal fix

Initialize `_apps_per_component` to zero and return from
`cacheElemToPostprocessorData()` until `initialSetup()` has computed it; then
clear `_cached_multiapp_pos_ids` and `_needed_postprocessors` before each real
rebuild. A focused AMR regression should cover both initial AMR and a later mesh
change, comparing mapped element values against current child positions.

## Collision status

As of upstream `next` HEAD `a75b6945b77ef4d783406982cea3e9ff753903a0`, exact
symbol searches for `cached_multiapp_pos_ids` and this transfer/cache lifecycle
did not return an upstream issue or PR. Related search hits concern ghosted
vector/active-solution tags and a separate FV adaptivity issue, not this cache
invariant. No upstream action taken.

## Gate status

- G01 hypothesis: PASS
- G02 environment: PASS (native Linux MOOSE AMR probe)
- G03 materiality: MATERIAL for AMR-coupled simulations
- G04 budget: CONTROLLED
- G05 evidence: PASS for native AMR crash; stale-cache mapping remains model-level
- G06: GO to staging review; no upstream authorization
