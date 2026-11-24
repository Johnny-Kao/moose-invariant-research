#!/usr/bin/env python3
"""Deterministic model of LibtorchArtificialNeuralNetTrainer::computeBatchSize."""


def production_compute_batch_size(num_samples, num_batches):
    if num_samples < num_batches:
        return 1
    if num_samples % num_batches == 0:
        return num_samples // num_batches
    sample_per_batch_1 = num_samples // num_batches
    remainder_1 = num_samples % num_batches
    sample_per_batch_2 = sample_per_batch_1 - 1
    # Mirrors the production expression, which divides by sample_per_batch_2.
    remainder_2 = num_samples - (num_samples // sample_per_batch_2) * sample_per_batch_2
    rel_remainder_1 = remainder_1 / sample_per_batch_1
    rel_remainder_2 = remainder_2 / sample_per_batch_2
    return sample_per_batch_2 if rel_remainder_2 > rel_remainder_1 else sample_per_batch_1


def fixed_compute_batch_size(num_samples, num_batches):
    if num_samples < num_batches:
        return 1
    if num_samples % num_batches == 0:
        return num_samples // num_batches
    sample_per_batch_1 = num_samples // num_batches
    if sample_per_batch_1 <= 1:
        return sample_per_batch_1
    remainder_1 = num_samples % num_batches
    sample_per_batch_2 = sample_per_batch_1 - 1
    remainder_2 = num_samples - (num_samples // sample_per_batch_2) * sample_per_batch_2
    return (sample_per_batch_2
            if remainder_2 / sample_per_batch_2 > remainder_1 / sample_per_batch_1
            else sample_per_batch_1)


def main():
    try:
        production_compute_batch_size(3, 2)
    except ZeroDivisionError:
        print("RED: 3 samples / 2 requested batches reaches zero batch-size divisor")
    else:
        raise AssertionError("production model unexpectedly avoided zero divisor")
    assert fixed_compute_batch_size(3, 2) == 1
    print("GREEN: guard returns a finite batch size for the same valid configuration")


if __name__ == "__main__":
    main()
