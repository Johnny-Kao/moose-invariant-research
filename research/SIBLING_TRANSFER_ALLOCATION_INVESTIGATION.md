# Sibling transfer allocation guard — rejected static lead

## Pinned source

- Upstream: `idaholab/moose`, branch `next`, `a75b6945b77ef4d783406982cea3e9ff753903a0`
- Research mirror: `Johnny-Kao/moose-invariant-research`, `main`, `f0a1d31a9b80e59b365488f90e75f26c85bce4b6`

## Initial hypothesis (rejected)

The initial readout suggested that sibling-transfer validators in `MultiAppCopyTransfer`,
`MultiAppPostprocessorTransfer`, `MultiAppPostprocessorToAuxScalarTransfer`,
`MultiAppReporterTransfer`, and `MultiAppScalarToAuxScalarTransfer` compare
`getFromMultiApp()->hasLocalApp(i)` with itself.

This was a transcription/readout error.  The checked source actually compares
source and target ownership in all five libMesh validators, and the MFEM
validator uses the equivalent `!=` comparison.

## Contract check

MOOSE's own `MultiAppCopyTransfer` documentation says sibling transfers require
the same number of children **and the same distribution on parallel processes**.
`max_procs_per_app` is a documented mechanism that can produce different rank
assignments.  The validator runs from `MultiAppTransfer::initialSetup()` before
the sibling transfer executes.

## Invariant status

For every global child index `i` and rank `r`:

```
source.hasLocalApp(i) == target.hasLocalApp(i)
```

The current expression is `source + target == 1`, so it rejects exactly the
mismatched ownership cases.

## Reproduction result

`research/sibling_transfer_allocation_repro.py` is a deterministic control test.
With two ranks and opposite ownership `[(True, False), (False, True)]`, the
current guard rejects both ranks.  The Research Actions run is the Linux
execution evidence.  No product regression is reproduced.

## Actual consequence

None established.  The invalid layout is rejected during setup as documented.

## Upstream collision

The earlier collision check against #33664 is not material because the proposed
sibling guard defect does not exist in the pinned source.

## Fix status

No production fix.  The control test is retained only to prevent a future
regression in this research branch.

## Maintainer acceptance rationale

No maintainer acceptance rationale applies; the lead is dropped.

## Current gate

- G01 hypothesis: FAIL (source readout contradicted by checked source)
- G02 environment: LIMITED (contract-level Linux control)
- G03 materiality: N/A
- G04 budget: CONTROLLED
- G05 evidence: SOUND for rejection of this lead
- G06 state: DROP; no staging or upstream action
