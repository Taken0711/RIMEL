#!/bin/bash
calc(){ awk "BEGIN { print "$*" }"; }
cat $1|jq 'to_entries|(.[]|.value.diff)' > tmp_deltas.txt
sums=`awk '{s+=$1} END {print s}' tmp_deltas.txt`
lineCount=`cat tmp_deltas.txt|wc -l`
res=`calc $sums/$lineCount`
echo "Complexité totale : $sums"
echo "Nombre de commit analysés : $lineCount"
echo "Complexité moyenne : $res"

