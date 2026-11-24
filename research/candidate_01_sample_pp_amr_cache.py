#!/usr/bin/env python3
"""Deterministic lifecycle model for candidate 01.

The model mirrors cacheElemToPostprocessorData() append behavior and execute()
consuming the cache from index zero. It is a cheap pre-build falsifier; the
MOOSE source-expression assertion in the workflow pins the production path.
"""


def cache_append(cache, current_mesh_mapping):
    cache.extend(current_mesh_mapping)


def execute_mapping(cache, active_element_count):
    return cache[:active_element_count]


def main():
    cache = []
    cache_append(cache, [0, 1])
    baseline = execute_mapping(cache, 2)
    assert baseline == [0, 1]

    # AMR changes element ordering/ownership mapping. The production method
    # appends, while execute() restarts at cache index 0.
    cache_append(cache, [2, 0, 1])
    buggy = execute_mapping(cache, 3)
    fixed_cache = [2, 0, 1]
    fixed = execute_mapping(fixed_cache, 3)
    assert buggy == [0, 1, 2]
    assert fixed == [2, 0, 1]
    assert buggy != fixed
    print("RED: post-AMR execute consumes stale pre-AMR cache prefix", buggy)
    print("GREEN: clearing cache before rebuild consumes current mapping", fixed)


if __name__ == "__main__":
    main()
