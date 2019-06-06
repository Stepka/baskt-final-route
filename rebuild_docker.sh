docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -a -q)
rm -r ./osrm-data
mkdir osrm-data
cd osrm-data
wget http://download.geofabrik.de/north-america/us/maryland-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/maryland-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/maryland-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/maryland-latest.osrm
cd ..
