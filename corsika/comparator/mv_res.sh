#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Pass result folder name as argument to this script"
	exit 1
fi
#mkdir ~/facultate/dizertatie/corsika-dizertatie/runs/$1
cp ~/facultate/dizertatie/corsika_input/SIM000001_coreas/* ~/facultate/dizertatie/corsika-dizertatie/runs/$1/SIM000001_coreas/

