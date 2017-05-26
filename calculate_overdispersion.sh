#!/usr/bin/env bash
R=$1
FILE=$2
OUTPUT=$3
$R --vanilla<<EOL
require('deepn')
Data <- importFromDeepn('$FILE')
out <- chooseFilter(Data, plot=FALSE)
write.csv(out, file='$OUTPUT', row.names=FALSE)
EOL
