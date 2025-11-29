FROM apache/airflow:2.10.5

RUN pip install --no-cache-dir astronomer-cosmos
RUN pip install --no-cache-dir dbt-core
RUN pip install --no-cache-dir dbt-trino
RUN pip install --no-cache-dir apache-airflow-providers-trino
RUN pip install --no-cache-dir protobuf==5.29.5