# bee-docker-compose-generator
python script to generate Docker-Compose.yml running multiple docker nodes.

## sample.yml
样例配置yml文件，生成的docker-compose.yml以此为模板。当升级image版本或修改配置时，需要更新此文件。

## .env
docker-compose 环境变量，需要修改BEE_SWAP_ENDPOINT为eth rpc节点地址，BEE_NETWORK_ID 当为testnet时值为10， mainnet时值为1

## init
环境初始化脚本，包括安装必要的python包。以sudo ./init 运行

## run脚本
初始化并运行节点

其中
result=`python3 gen-docker-compose.py --datapath /opt/chia/l1 -c 64`
-datapath为节点volume数据存储位置， -c 表示节点数量

echo $result | xargs python3 export_key.py -d 
导出public key及private key，方便备份

python3 batch_send_transaction.py -r http://172.16.4.40:19000 -k your_key -bzz 0 -eth 0.01
-r 为eth rpc节点地址， your_key为发送交易的钱包私钥，主网不需要质押bzz，因为设为0，eth用于支付gas手续费
