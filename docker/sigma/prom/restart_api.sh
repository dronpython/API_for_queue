echo "Stopping DevOpsAPI container"
docker-compose down 
echo "Starting DevOpsAPI container"
docker-compose up --build -d