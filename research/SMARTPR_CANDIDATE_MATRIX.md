# MOOSE SmartPR candidate matrix

This matrix is the current research handoff. The upstream base is
`idaholab/moose/next` at `a75b6945b77ef4d783406982cea3e9ff753903a0`; current-source
assertions were fetched directly from that commit in [GC run 45472771118](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45472771118).

| Candidate | Production invariant | RED/GREEN evidence | Minimal regression |
| --- | --- | --- | --- |
| Sample postprocessor transfer | AMR rebuild replaces the element→subapp cache; it must not append stale entries | [45471920306](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45471920306) | Native MultiApp transfer with one AMR change; compare postprocessor values before/after rebuild |
| Peridynamics spacing | Every converted element gets finite spacing/horizon data; boundary-only elements currently divide by zero | [45471566219](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45471566219) | One isolated converted element must produce a targeted diagnostic; two connected elements remain finite |
| libtorch ANN batches | A valid `num_samples >= num_batches >= 1` request must never create a zero divisor | [45470911015](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45470911015) | Native trainer `(3,2)` plus divisible and samples-less-than-batches controls |
| Bayesian active learner | Empty finite likelihood set must fail explicitly, not publish NaN convergence | [45471574817](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45471574817) | All-NaN likelihood regression plus mixed finite/NaN control |
| Shaft-connected compressor | Interpolation/extrapolation requires two bracketing map points | [45470918068](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45470918068) | One-point table must reject or take explicit constant branch; two-point interpolation control |

All five have exact-symbol open/closed issue and PR searches with no collision at the
current base. None has been published upstream. The remaining gate is native MOOSE or
module execution on GC; the source-equivalent harnesses are deliberately labeled as
such and are not being presented as final product regressions.
