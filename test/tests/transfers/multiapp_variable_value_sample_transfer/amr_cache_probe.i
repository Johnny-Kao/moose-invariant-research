!include full_domain_primary.i

# Force a real mesh-change callback after the transfer has built its initial
# element-to-subapplication cache.  The existing full-domain round trip makes
# the transferred-back value observable through subapp_primary_diff.
[Adaptivity]
  initial_marker = uniform
  initial_steps = 1
[]

[Postprocessors]
  [diff_average]
    type = ElementAverageValue
    variable = subapp_primary_diff
    execute_on = 'initial timestep_end'
  []
[]

[Outputs]
  csv = true
  file_base = amr_cache_probe_out
[]
