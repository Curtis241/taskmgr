#!/bin/bash

COUNT=$1

add_tasks(){
  local MAX="$1"
  for i in `seq 1 $MAX`;
  do
    tm add "Task${i}"
  done
}

add_tasks_with_random_date(){
  local MAX="$1"
  for i in `seq 1 $MAX`;
  do
    rnd_day=$((1 + RANDOM % 30))
    tm add "Task${i}" -d "dec ${rnd_day}"
  done
}

[ $# -eq 0 ] && { echo "Usage: $0 max count"; exit 1; }

SECONDS=0
#add_tasks "$COUNT"
add_tasks_with_random_date "$COUNT"
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
