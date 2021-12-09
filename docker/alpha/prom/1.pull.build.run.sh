cd /u01/project/devopsapi_prom/ # в пром альфе - папка называется project, в отличии от прома сигмы...
git init
echo "Git checkout MASTER"
git checkout master
git reset --hard
echo "Git pull..."
git pull
cd /u01/project/devopsapi_prom/docker/alpha/prom
# for refresh info about commit
git pull
echo "mkdir libs..."
mkdir ../../../libs/
echo "Copy all data from libs to libs..."
cp /u01/project/devopsapi_prom/libs/* ../../../libs/
echo "Copy yamls..."
cp -r /u01/project/devopsapi_configs/yamls/devopsapi/docker/* ../../../docker/
echo "docker-compose up --build..."
docker-compose up --build