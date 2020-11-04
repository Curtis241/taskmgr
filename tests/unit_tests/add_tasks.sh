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
    rnd_day=$((1 + RANDOM % 29))
    tm add "Task${i}" -d "mar ${rnd_day}"
  done
}

complete_tasks(){
  local MAX="$1"
  for i in `seq 1 $MAX`;
  do
    rnd_task_id=$((1 + RANDOM % $MAX))
    tm complete ${rnd_task_id}
  done
}

delete_tasks(){
  local MAX="$1"
  for i in `seq 1 $MAX`;
  do
    rnd_task_id=$((1 + RANDOM % $MAX))
    tm delete ${rnd_task_id}
  done
}

simulate_user(){
  local MAX="$1"
  for i in `seq 1 $MAX`;
  do
    rnd_day=$((1 + RANDOM % 29))
    tm add "Task${i}" -d "mar ${rnd_day}"
    #complete_task_id=$((1 + RANDOM % $MAX))
    #tm complete ${complete_task_id}
    #delete_task_id=$((1 + RANDOM % $MAX))
    #tm delete ${delete_task_id}
    #tm count all --silent
  done
}


[ $# -eq 0 ] && { echo "Usage: $0 max count"; exit 1; }

SECONDS=0
#add_tasks "$COUNT"
add_tasks_with_random_date "$COUNT"
#complete_tasks "$COUNT"
#simulate_user "$COUNT"
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
