CLUSTER_NAME=$1
TASK_DEFINITION=$2
SUBNET_ID=$3
SECURITY_GROUP_ID=$4

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "引数を指定してください"
    exit 1
fi

aws ecs run-task \
    --cluster $CLUSTER_NAME \
    --task-definition $TASK_DEFINITION \
    --count 1 \
    --launch-type FARGATE \
    --network-configuration \
    "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}"