filename=$1
stacknaem=$2

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "引数を指定してください"
    exit 1
fi

aws cloudformation deploy \
    --template-file $1 \
    --stack-name $2 \
    --capabilities CAPABILITY_NAMED_IAM