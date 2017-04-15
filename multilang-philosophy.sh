#!/bin/bash

NUM=10
if [[ $@ -ge 1 ]]; then
  NUM=$1
fi

LANG=(en de it fr es sv ceb nl)
for l in ${LANG[@]}; do
  ./WikiCrawler.py -l $l -n $NUM | tee results/philosophy/$l
done
