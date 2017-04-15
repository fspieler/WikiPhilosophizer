#!/bin/bash

NUM=10
if [[ $@ -ge 1 ]]; then
  NUM=$1
fi

LANG=(de it fr es sv ceb nl en)
for l in ${LANG[@]}; do
  ./FindPopularArticles.py -l $l -n $NUM -t 100 | tail -n `expr 5 + $NUM` > results/top-words/$l
done
