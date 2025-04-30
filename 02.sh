current_time=$(date +"%Y%m%d")
name="02_write_mongo"
nohup python $name.py \
        > "$name_$current_time".log 2>&1 & \
        echo $! >"$name_$current_time".pid

