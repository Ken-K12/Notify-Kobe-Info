filename=$1
stacknaem=$2

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "引数を指定してください"
    exit 1
fi

# .envファイルの読み込み
set -o allexport
source ../app/.env
set +o allexport

# 一時ファイルの作成
tempfile=$(mktemp)

# テンプレートファイルの変数を置換して一時ファイルに保存
envsubst < $filename > $tempfile

aws cloudformation deploy \
    --template-file $tempfile \
    --stack-name $stacknaem \
    --capabilities CAPABILITY_NAMED_IAM

# 一時ファイルを削除
rm $tempfile