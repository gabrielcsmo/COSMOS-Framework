#include <stdio.h>
#include <stdlib.h>

static long num_steps;
static double step;

int main (int argc, char **argv)
{
	int i;
	double x;
	double pi;
	double sum = 0.0;

	if (argc != 2) {
		fprintf(stderr, "Usage: pi <steps>\n");
		return -1;
	}

	num_steps = atol(argv[1]);
	step = 1.0 / ( double ) num_steps;

	for ( i = 1; i <= num_steps; i++){
		x = ( i - 0.5 ) * step;
		sum = sum + 4.0 / ( 1.0 + x * x );
	}
	pi = step * sum;

	printf( "The computed value of pi is %f\n", pi );
	return 0;
}

