# Candidate 02 — undefined peridynamic spacing for an isolated converted element

## Hypothesis

`PeridynamicsMesh::createPeridynamicsMeshData()` computes
`_pdnode_average_spacing[id] = dist_sum / n_fe_neighbors` without handling
`n_fe_neighbors == 0`. `MeshGeneratorPD` permits selecting arbitrary FE blocks,
including a block containing one isolated element.

## Production reachability

The converted-element set is built from the user-selected `blocks_to_pd`/`blocks_as_fe`
sets; there is no neighbor-count precondition in `MeshGeneratorPD`. A one-element
block or disconnected component therefore reaches the division with zero neighbors.

## Violated invariant

Every stored spacing and any horizon derived from `horizon_number` must be finite and
positive before bond construction and constitutive calculations.

## Reproduction result

Research Actions model `candidate_02_peridynamics_zero_neighbors.py` reproduces the
zero-neighbor path as RED and verifies a minimal explicit rejection as GREEN. This is
currently a deterministic source-contract model; native peridynamics integration is
still required before staging. A follow-up Linux C++ floating-point harness also
passed in [45471566219](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45471566219).

## Actual consequence

The spacing becomes NaN/Inf. With `horizon_number`, the horizon radius is undefined;
neighbor/bond discovery can silently produce no bonds or propagate non-finite values
into peridynamic response calculations.

## Minimal fix / regression

Reject `n_fe_neighbors == 0` with a targeted error (or define and document a finite
single-point spacing policy) before the division. Add a mesh-generator regression with
one selected isolated element and assert the explicit diagnostic, plus a normal
two-element case that remains finite.

## Collision status

Exact symbol searches (`n_fe_neighbors`, `pdnode_average_spacing`) and related issue
searches found no exact upstream issue/PR at `next` HEAD
`a75b6945b77ef4d783406982cea3e9ff753903a0`. Existing peridynamics singular-shape
tensor issue #15394 is a different downstream invariant.

## Gate status

- G01 hypothesis: PASS
- G02 environment: LIMITED (contract model only)
- G03 materiality: PROVISIONAL; native integration required
- G04 collision: no exact collision found
- G05 evidence: LIMITED
- G06: GO to native GC validation
