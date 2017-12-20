#!/bin/sh

sl=12

if [ "$#" -ne 3 ]
then
    echo "Usage: $0 [FOLLOWERS] [OPPORTUNISTS] [LEADERS]" >&2
    exit 1
fi 

echo "Clearing existing knowledge bases ..."
rm agent-kbs/*.pl
echo "Clearing existing log files ..."
rm screenlog.0
echo "Done!"

j=0
if test $1 -gt 0
then
	echo "Running extremist followers:"

	for i in $(seq 1 $1)
	do
	    screen -L -dmS extremist_follower$i ./TMWhlinterface.py --name $i  --role extremist_follower
	    echo "Extremist follower no $i started!"
	    j=$i
	    sleep $sl
	done
fi

if test $2 -gt 0
then
	echo "Running opportunists:"

	k=$(($j+$2))
	j=$((j+1))

	for i in $(seq $j $k)
	do
	    screen -L -dmS opportunist$i ./TMWhlinterface.py --name $i   --role opportunist
	    echo "Opportunist no $i started!"
	    j=$i
	    sleep $sl
	done
fi

if test $3 -gt 0
then
	echo "Running leaders:"

	k=$(($j+$3))
	j=$((j+1))

	for i in $(seq $j $k)
	do
	    screen -L -dmS leader$i ./TMWhlinterface.py --name $i  --role leader
	    echo "Leader no $i started!"
	    sleep $sl
	done
fi
