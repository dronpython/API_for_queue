cd /u01/projects/devopsapi_dev/
git init
echo "Git checkout autoexecutor"
git checkout autoexecutor
git reset --hard
echo "Git pull..."
git pull
cd /u01/projects/devopsapi_dev/docker/sigma/dev
# for refresh info about commit
git pull
echo "mkdir libs..."
mkdir ../../../libs/
echo "Copy all data from libs to libs..."
cp /u01/projects/devopsapi_configs/libs/* ../../../libs/
echo "Copy yamls..."
cp -r /u01/projects/devopsapi_configs/yamls/devopsapi/docker/* ../../../docker/
#echo "docker-compose build..."
#docker-compose build
echo "docker-compose up --build..."
docker-compose up --build
