# Nifi Ingestion

## How to run

```bash
cd ingestion/nifi
mkdir lib
cd lib
curl -LfO 'https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-processors-nar/1.28.1/nifi-iceberg-processors-nar-1.28.1.nar'
curl -LfO 'https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-services-nar/1.28.0/nifi-iceberg-services-nar-1.28.0.nar'
curl -LfO 'https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-services-api-nar/1.28.1/nifi-iceberg-services-api-nar-1.28.1.nar'

curl -LfO 'https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/9.5.0/mysql-connector-j-9.5.0-javadoc.jar'
curl -LfO 'https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.8/postgresql-42.7.8-all.jar'
```


