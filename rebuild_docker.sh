docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -a -q)
docker build -t final_route .
docker run -d -p 80:5000 final_route
