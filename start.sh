#!/bin/sh

docker compose up -d

echo "Kafka Connect files will change now\n"
docker compose exec kafka-connect sed -i 's/localhost:9092/kafka:29092/' etc/kafka/connect-standalone.properties
docker compose exec kafka-connect sed -i 's/key.converter.schemas.enable=true/key.converter.schemas.enable=false/' etc/kafka/connect-standalone.properties
docker compose exec kafka-connect sed -i 's/value.converter.schemas.enable=true/value.converter.schemas.enable=false/' etc/kafka/connect-standalone.properties
docker compose exec kafka-connect bash -c "echo 'rest.port=8082' >> etc/kafka/connect-standalone.properties"
docker compose exec kafka-connect sed -i 's/localhost/elasticsearch/' etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties
docker compose exec kafka-connect bash -c "echo 'schema.ignore=true' >> etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties"
#docker compose exec kafka-connect bash -c "echo 'transforms.renameTopic.type: org.apache.kafka.connect.transforms.RegexRouter' >> etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties"
#docker compose exec kafka-connect bash -c "echo 'transforms: renameTopic' >> etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties" 
#docker compose exec kafka-connect bash -c "echo 'transforms.renameTopic.regex: .*' >> etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties" 
#docker compose exec kafka-connect bash -c "echo 'transforms.renameTopic.replacement: elasticsearch_index_name' >> etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties"
docker compose exec kafka-connect bash -c "echo 'auto.create.indices.at.start: false' >> etc/kafka-connect-elasticsearch/quickstart-elasticsearch.properties"

cd src

echo "kafka-connect step starts!"

python3 kafka-connect.py

