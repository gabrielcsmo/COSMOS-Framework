#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>

#define RANGE 1
#define get_rand_double(limit) ((((double)rand()) / RAND_MAX) * (2 * limit) - limit)
#define SAFE_ASSERT(condition, message) while(condition) {	\
	perror(message);		\
	goto failure;			\
}

double* multiply(int N, double *A, double* B) {
	double *C = (double *) calloc(sizeof(double), N*N);
	if (C == NULL)
		return NULL;
	
	int i, j, k;
	for (i = 0; i < N; ++i)
		for (j = 0; j < N; ++j)
			for (k = 0; k < N; ++k)
				C[i*N+j] += A[i*N+k] * B[k*N+j];

	return C;
}

int generate_data(int N, double **A) {
	int i, j;
	double *aux;

	*A = malloc(N * N * sizeof(double));
	SAFE_ASSERT(*A == 0, "Failed malloc");

	aux = *A;

	srand(time(0));

	for (i = 0; i < N; ++i) {
		for ( j = 0; j < N; ++j) {
			aux[i * N + j] = get_rand_double(RANGE);
		}
	}

	return 0;

failure:
	return -1;
}

int main(int argc, char **argv) {
	double *A, *B, *res;
	int ret, N;
	clock_t start, end;

	if (argc < 2) {
		printf("At least 1 argument required: N - matrix size\n");
		exit(1);
	}

	N = atoi(argv[1]);

	ret = generate_data(N, &A);
	if (ret < 0)
		return ret;

	ret = generate_data(N, &B);
	if (ret < 0)
		return ret;
	
	start = clock();
	res = multiply(N, A, B);
	end = clock();
	printf("Time: %f\n", ((double)(end - start)/CLOCKS_PER_SEC));
	if (A) {
		free(A);
	}
	if (B) {
		free(B);
	}
	if (res) {
		free(res);
	}

	return 0;
}
