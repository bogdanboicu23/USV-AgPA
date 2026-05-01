#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <mpi.h>

void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

int partition(int *arr, int lo, int hi) {
    int pivot = arr[hi];
    int i = lo - 1;
    for (int j = lo; j < hi; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[hi]);
    return i + 1;
}

void quicksort(int *arr, int lo, int hi) {
    if (lo < hi) {
        int p = partition(arr, lo, hi);
        quicksort(arr, lo, p - 1);
        quicksort(arr, p + 1, hi);
    }
}

/* Merge two sorted arrays into a new allocated array */
int *merge(int *a, int na, int *b, int nb) {
    int *result = malloc((na + nb) * sizeof(int));
    int i = 0, j = 0, k = 0;
    while (i < na && j < nb) {
        if (a[i] <= b[j])
            result[k++] = a[i++];
        else
            result[k++] = b[j++];
    }
    while (i < na) result[k++] = a[i++];
    while (j < nb) result[k++] = b[j++];
    return result;
}

int is_sorted(int *arr, int n) {
    for (int i = 1; i < n; i++) {
        if (arr[i] < arr[i - 1])
            return 0;
    }
    return 1;
}

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc != 2) {
        if (rank == 0)
            fprintf(stderr, "Usage: %s <N>\n", argv[0]);
        MPI_Finalize();
        return 1;
    }

    int n = atoi(argv[1]);

    /* Pad n so it's divisible by size */
    int padded_n = n;
    if (n % size != 0)
        padded_n = n + (size - n % size);

    int chunk_size = padded_n / size;
    int *data = NULL;

    if (rank == 0) {
        data = malloc(padded_n * sizeof(int));
        srand(42);
        for (int i = 0; i < n; i++)
            data[i] = rand() % 1000000;
        /* Fill padding with INT_MAX so they sort to the end */
        for (int i = n; i < padded_n; i++)
            data[i] = __INT_MAX__;
    }

    int *local = malloc(chunk_size * sizeof(int));

    double t_start = MPI_Wtime();

    /* Scatter data to all processes */
    MPI_Scatter(data, chunk_size, MPI_INT,
                local, chunk_size, MPI_INT,
                0, MPI_COMM_WORLD);

    /* Each process sorts its local chunk */
    quicksort(local, 0, chunk_size - 1);

    /* Tree-based pairwise merge */
    int local_size = chunk_size;
    int step = 1;
    while (step < size) {
        if (rank % (2 * step) == 0) {
            int partner = rank + step;
            if (partner < size) {
                int recv_size;
                MPI_Recv(&recv_size, 1, MPI_INT, partner, 0,
                         MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                int *recv_buf = malloc(recv_size * sizeof(int));
                MPI_Recv(recv_buf, recv_size, MPI_INT, partner, 1,
                         MPI_COMM_WORLD, MPI_STATUS_IGNORE);

                int *merged = merge(local, local_size, recv_buf, recv_size);
                free(local);
                free(recv_buf);
                local = merged;
                local_size += recv_size;
            }
        } else {
            int target = rank - step;
            MPI_Send(&local_size, 1, MPI_INT, target, 0, MPI_COMM_WORLD);
            MPI_Send(local, local_size, MPI_INT, target, 1, MPI_COMM_WORLD);
            break;
        }
        step *= 2;
    }

    double t_end = MPI_Wtime();

    if (rank == 0) {
        /* Remove padding elements */
        int final_n = (padded_n == n) ? n : n;
        if (!is_sorted(local, final_n)) {
            fprintf(stderr, "ERROR: array is not sorted!\n");
        } else {
            printf("MPI %d %d %.6f\n", size, n, t_end - t_start);
        }
        free(data);
    }

    free(local);
    MPI_Finalize();
    return 0;
}
