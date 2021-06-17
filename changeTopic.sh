#!/bin/bash

echo "$1"
echo "$2"
#echo "$3"

docker compose exec kafka-connect sed -i "s/$1/$2/" etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties

echo "Elasticsearch sink connection will be established!"

#docker compose exec kafka-connect bash -c "echo 'transforms.renameTopic.replacement: $3' >> etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties"

docker exec kafka-connect connect-standalone etc/kafka/connect-standalone.properties  etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties
