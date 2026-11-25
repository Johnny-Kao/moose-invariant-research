# Staging recommendation

## First candidate: AMR setup/cache lifecycle in `MultiAppVariableValueSamplePostprocessorTransfer`

This is the strongest SmartPR candidate among the five because it is a native
AMR crash in a normal framework execution path, with a second silent-cache
invariant in the same function. Initial AMR can call `meshChanged()` before
`initialSetup()` assigns `_apps_per_component`; the cache builder then divides by
zero and aborts the process. Later rebuilds append to
`_cached_multiapp_pos_ids`, so an active-element reorder can still map values to
the wrong element or array component.

The proposed patch is small and local: defer cache work until setup has computed
the grouping, then clear the current mapping before each real rebuild. The native
unmodified AMR probe reproduced the FPE in
[45449298449](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45449298449);
the fixed source completed the same build, baseline, and AMR probe with finite
output in [45559576212](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45559576212).
The exact current-upstream source check remains green in
[45472771118](https://github.com/Johnny-Kao/moose-invariant-research/actions/runs/45472771118).

This is ready for staging review, not upstream publication. The stale-prefix
part still needs a focused native value-mapping regression before being claimed
as independently reproduced; the setup-order FPE is fully native RED/GREEN.
