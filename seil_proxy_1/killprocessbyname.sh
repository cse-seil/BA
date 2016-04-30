#!/bin/bash

IFS='\n'
var=$(ps aux | grep $1)
for i in $var
do
tt=$(echo $i | awk '{print $2}')
kill -9 $tt
done
