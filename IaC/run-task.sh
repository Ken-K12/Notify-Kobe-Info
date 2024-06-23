clustername=$1
taskdefinitionname=$2

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "引数を指定してください"
    exit 1
fi

aws ecs run-task \
    --cluster  $1\
    --task-definition $2 \
    --count 1 \
    --launch-type FARGATE