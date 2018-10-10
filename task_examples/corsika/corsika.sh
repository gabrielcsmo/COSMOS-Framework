# This script assumes that you already have corsika compiled
# in /home/`whoami` folder and corsika input in /home/`whoami`
# This script creates another folder with $1 name in home folder
# and replaces "taskparam" string in RUN000001.inp
# "taskparam" should be the DIRECT variable in RUN000001.inp file

if [ $# -eq 0 ]
	then
		echo "No args were passed"
		exit -1
fi

TASK=/home/`whoami`/$1
ME=`whoami`
INP=$2

if [[ -z "$INP" ]]
	then
		echo "INPUT is missing"
		exit -1
fi

rm -rf $TASK
mkdir -p $TASK
cp -rf ~/corsika* $TASK
rm -rf $TASK/corsika_input/DAT000001* $TASK/corsika_input/SIM000001_coreas
cd $TASK/corsika/run
sed "s/taskparam/\/home\/$ME\/$1\/corsika_input\//" < $INP > _$INP
mv _$INP $INP
cp $INP $TASK/corsika_input/
#pwd
#cat $INP

./corsika75600Linux_QGSII_gheisha_thin_coreas < $INP  > $TASK/$INP.log
