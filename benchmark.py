#!/usr/bin/env python3
"""Benchmark sequential vs MPI Quick Sort and generate performance graphs."""

import subprocess
import re
import sys
import matplotlib.pyplot as plt

SIZES = [100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
MPI_PROCS = [1, 2, 4]
RUNS = 3  # average over multiple runs


def run_seq(n):
    """Run sequential quicksort and return elapsed time."""
    times = []
    for _ in range(RUNS):
        result = subprocess.run(
            ["./quicksort_seq", str(n)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            print(f"  SEQ error for N={n}: {result.stderr.strip()}")
            return None
        match = re.search(r"SEQ \d+ ([\d.]+)", result.stdout)
        if match:
            times.append(float(match.group(1)))
    return sum(times) / len(times) if times else None


def run_mpi(n, nprocs):
    """Run MPI quicksort and return elapsed time."""
    times = []
    for _ in range(RUNS):
        result = subprocess.run(
            ["mpirun", "--oversubscribe", "-np", str(nprocs), "./quicksort_mpi", str(n)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            print(f"  MPI error for N={n}, np={nprocs}: {result.stderr.strip()}")
            return None
        match = re.search(r"MPI \d+ \d+ ([\d.]+)", result.stdout)
        if match:
            times.append(float(match.group(1)))
    return sum(times) / len(times) if times else None


def main():
    # Build first
    print("Building...")
    subprocess.run(["make", "all"], check=True)

    # Collect results
    seq_times = {}
    mpi_times = {np: {} for np in MPI_PROCS}

    for n in SIZES:
        label = f"{n:,}"
        print(f"N = {label}")

        t = run_seq(n)
        if t is not None:
            seq_times[n] = t
            print(f"  SEQ: {t:.4f}s")

        for np in MPI_PROCS:
            t = run_mpi(n, np)
            if t is not None:
                mpi_times[np][n] = t
                print(f"  MPI (np={np}): {t:.4f}s")

    # --- Graph 1: Execution time vs array size ---
    fig, ax = plt.subplots(figsize=(10, 6))

    sizes_k = [n / 1000 for n in SIZES]
    size_labels = [f"{n // 1000}K" if n < 1_000_000 else f"{n // 1_000_000}M" for n in SIZES]

    if seq_times:
        ax.plot(sizes_k, [seq_times.get(n, float('nan')) for n in SIZES],
                'o-', label='Secvential', linewidth=2)

    for np in MPI_PROCS:
        if mpi_times[np]:
            ax.plot(sizes_k, [mpi_times[np].get(n, float('nan')) for n in SIZES],
                    's--', label=f'MPI (np={np})', linewidth=2)

    ax.set_xlabel('Dimensiunea tabloului (x1000)', fontsize=12)
    ax.set_ylabel('Timpul de executare (secunde)', fontsize=12)
    ax.set_title('Quick Sort: Timp de executare vs Dimensiune', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig('graph_time.png', dpi=150)
    print("Saved graph_time.png")

    # --- Graph 2: Speedup vs number of processes ---
    largest = SIZES[-1]
    fig2, ax2 = plt.subplots(figsize=(8, 5))

    if largest in seq_times:
        t_seq = seq_times[largest]
        procs = []
        speedups = []
        for np in MPI_PROCS:
            if largest in mpi_times[np]:
                procs.append(np)
                speedups.append(t_seq / mpi_times[np][largest])

        ax2.plot(procs, speedups, 'o-', linewidth=2, markersize=8, label='Speedup real')
        ax2.plot(procs, procs, 'k--', alpha=0.5, label='Speedup ideal (liniar)')
        ax2.set_xlabel('Numar de procese', fontsize=12)
        ax2.set_ylabel('Speedup', fontsize=12)
        ax2.set_title(f'Speedup MPI Quick Sort (N={largest:,})', fontsize=14)
        ax2.set_xticks(MPI_PROCS)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('graph_speedup.png', dpi=150)
    print("Saved graph_speedup.png")


if __name__ == "__main__":
    main()
