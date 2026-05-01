CC = clang
MPICC = mpicc
CFLAGS = -O2 -Wall -arch arm64

all: seq mpi

seq: quicksort_seq.c
	$(CC) $(CFLAGS) -o quicksort_seq quicksort_seq.c

mpi: quicksort_mpi.c
	$(MPICC) $(CFLAGS) -o quicksort_mpi quicksort_mpi.c

clean:
	rm -f quicksort_seq quicksort_mpi

.PHONY: all seq mpi clean
