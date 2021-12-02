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
    if [[ $rnd_day -lt 10 ]]
    then
      day_text="0${rnd_day}"
    else
      day_text="${rnd_day}"
    fi

    rnd_month=$((1 + RANDOM % 12))
    if [[ $rnd_month -lt 10 ]]
    then
      month_text="0${rnd_month}"
    else
      month_text="${rnd_month}"
    fi
    echo "Added text on 2021-${month_text}-${day_text}"
    tm add "Task${i}" -d "2021-${month_text}-${day_text}"
  done
}

complete_tasks(){
  local MAX="$1"
  for i in `seq 1 $MAX`;
  do
    rnd_task_id=$((1 + RANDOM % $MAX))
    echo "Complete task $rnd_task_id"
    tm complete ${rnd_task_id}
  done
}

delete_tasks(){
  local MAX="$1"
  for i in `seq 1 $MAX`;
  do
    rnd_task_id=$((1 + RANDOM % $MAX))
    echo "Delete task $rnd_task_id"
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
#add_tasks_with_random_date "$COUNT"
#complete_tasks "$COUNT"
#simulate_user "$COUNT"
delete_tasks "$COUNT"
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
