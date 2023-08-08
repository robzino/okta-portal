
# http://localhost:5000/
#


NAME=okta-portal
id=`docker ps | grep "$NAME" | awk {'print $1'}`
docker stop $id

docker build -t $NAME:latest .

docker run -d -e TOKEN=$TOKEN -e URLBASE=$URLBASE -p 5000:5000 $NAME
