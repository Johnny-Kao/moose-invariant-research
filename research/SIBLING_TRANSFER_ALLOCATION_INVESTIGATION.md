# Sibling transfer allocation guard — independent investigation

## Pinned source

- Upstream: `idaholab/moose`, branch `next`, `09f3b86652118bc759d889fe0235434c4bb02a54`
- Research mirror: `Johnny-Kao/moose-invariant-research`, `main`, `f0a1d31a9b80e59b365488f90e75f26c85bce4b6`

## Hypothesis

The sibling-transfer validators in `MultiAppCopyTransfer`,
`MultiAppPostprocessorTransfer`, `MultiAppPostprocessorToAuxScalarTransfer`,
`MultiAppReporterTransfer`, and `MultiAppScalarToAuxScalarTransfer` compare
`getFromMultiApp()->hasLocalApp(i)` with itself.  The intended contract is to
compare source and target ownership for the same child index.

## Production reachability

MOOSE's own `MultiAppCopyTransfer` documentation says sibling transfers require
the same number of children **and the same distribution on parallel processes**.
`max_procs_per_app` is a documented mechanism that can produce different rank
assignments.  The validator runs from `MultiAppTransfer::initialSetup()` before
the sibling transfer executes.

## Violated invariant

For every global child index `i` and rank `r`:

```
source.hasLocalApp(i) == target.hasLocalApp(i)
```

The current expression is `source + source == 1`, which is false for both
possible values of `source`; it cannot detect any mismatch.

## Reproduction result

`research/sibling_transfer_allocation_repro.py` is a deterministic control-flow
reproducer.  With two ranks and opposite ownership `[(True, False), (False,
True)]`, the current guard accepts both ranks.  The copy transfer's execution
condition (`source local && target local`) is false on both ranks, so the target
value remains stale.  The one-token correction to `source + target == 1`
rejects both ranks.  The Research Actions run is the authoritative Linux
execution evidence; this is deliberately not presented as a full MOOSE binary
integration run.

## Actual consequence

This is a correctness failure, not merely a missing diagnostic: an illegal
sibling layout can silently leave copied field values unchanged.  In a coupled
simulation, the receiving sibling can advance using the previous timestep's or
initial value.  Postprocessor/scalar/reporter siblings use analogous ownership
conditions and can likewise omit updates.

## Upstream collision

Searches of current issues/PRs and recent commits found #33664, which adds a
communicator-size check for parent/sub-app `MultiAppDofCopyTransfer`; it does not
fix sibling ownership validation.  No exact prior issue/PR or merged fix for
this repeated-self comparison was found.  This remains a research candidate,
not an upstream claim.

## Minimal fix and regression test

Replace the second `getFromMultiApp()->hasLocalApp(i)` with
`getToMultiApp()->hasLocalApp(i)` in the five affected validators (the MFEM
copy validator uses the equivalent `!=` form).  Add a two-rank sibling test with
opposite child ownership that must fail during `initialSetup`, plus a matched
ownership control that continues to transfer.

## Maintainer acceptance rationale

The fix is five one-token corrections plus a focused MPI regression.  It makes
the implementation enforce an already documented precondition, prevents silent
stale coupling data, and does not alter valid matched-partition transfers.

## Current gate

- G01 hypothesis: PASS
- G02 environment: LIMITED (contract-level Linux test; full MOOSE build not run)
- G03 materiality: MATERIAL if the documented sibling layout is used
- G04 budget: CONTROLLED
- G05 evidence: LIMITED until native MOOSE MPI integration test
- G06 state: GO for native Linux/MPI validation; no staging or upstream action
