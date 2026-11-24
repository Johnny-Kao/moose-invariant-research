# Candidate 01 — stale element→postprocessor cache after AMR

## Hypothesis

`MultiAppVariableValueSamplePostprocessorTransfer::cacheElemToPostprocessorData()`
appends to `_cached_multiapp_pos_ids` on every call, including calls from
`meshChanged()`, but never clears the vector. `execute()` always starts at
`_cached_multiapp_pos_ids[0]` while iterating the current active elements.

## Production reachability

The transfer implements `MeshChangedInterface`; `meshChanged()` directly calls
the cache builder after mesh changes. Adaptive mesh refinement/coarsening is a
normal MOOSE execution path. The transfer is used to map sub-application
postprocessors back onto a parent constant-monomial auxiliary variable.

## Violated invariant

The cache must have exactly one current entry per current active element (and
component grouping), in the same iteration order used by `execute()`. A rebuild
must replace, not append to, the previous mapping.

## Reproduction result

The Research Actions model in `candidate_01_sample_pp_amr_cache.py` reproduces
the lifecycle: pre-AMR mapping `[0, 1]`, post-AMR mapping `[2, 0, 1]`; baseline
execution consumes stale prefix `[0, 1, 2]`, while clearing before rebuild gives
`[2, 0, 1]`. This is a contract-level RED/GREEN model, not yet a full MOOSE
binary integration test.

## Actual consequence

After AMR, postprocessor values can be written to the wrong parent elements or
array components. The simulation continues with silently corrupted coupling
data; no bounds error is required.

## Minimal fix

At the start of `cacheElemToPostprocessorData()`, clear
`_cached_multiapp_pos_ids` and `_needed_postprocessors` before rebuilding. A
focused AMR regression should run the transfer before and after mesh change and
compare the mapped element values against the current child positions.

## Collision status

As of upstream `next` HEAD `09f3b86652118bc759d889fe0235434c4bb02a54`, exact
symbol searches for `cached_multiapp_pos_ids` and this transfer/cache lifecycle
did not return an upstream issue or PR. Related search hits concern ghosted
vector/active-solution tags and a separate FV adaptivity issue, not this cache
invariant. No upstream action taken.

## Gate status

- G01 hypothesis: PASS
- G02 environment: LIMITED until native MOOSE GC test
- G03 materiality: MATERIAL for AMR-coupled simulations
- G04 budget: CONTROLLED
- G05 evidence: LIMITED (source + deterministic lifecycle model)
- G06: GO to native GC validation; no staging/upstream authorization
