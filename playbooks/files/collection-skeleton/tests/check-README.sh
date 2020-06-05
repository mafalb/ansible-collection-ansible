#!/bin/bash

ret=0

for role in roles/*
do
	ls $role/README.md || ret=1
done

exit $ret
