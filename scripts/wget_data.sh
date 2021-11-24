#!/bin/bash
wget https://database.lichess.org/standard/list.txt
while read line; do wget $line; done < list.txt
