from datetime import datetime
from cosmos import DbtDag, ProjectConfig, ProfileConfig

# -----------------------------
# Đường dẫn project dbt
# -----------------------------
project_path = "/opt/airflow/dbt/dbt_project"


# -----------------------------
# DAG parameters
# -----------------------------
default_args = {
    "start_date": datetime(2024, 1, 1),
    "retries": 3
}



# -----------------------------
# ProfileConfig dùng profiles.yml nằm trong container
# -----------------------------
profile_config = ProfileConfig(
    profile_name="dbt_project",   # trùng với profiles.yml
    target_name="dev",            # trùng với profiles.yml
    profiles_yml_filepath="/opt/airflow/dbt/dbt_project/profiles.yml"
)


# -----------------------------
# DbtDag Cosmos
# -----------------------------
dbt_pipeline = DbtDag(
    dag_id="dbt_pipeline",
    project_config=ProjectConfig(project_path),
    profile_config=profile_config,
    # Airflow
    default_args=default_args,
    schedule="@daily",
    catchup=False,
    max_active_runs=1,

    # Cosmos
    tags=["dbt"],
    # models=[
    #     "bronze.*",
    #     "silver_*",
    #     "gold_*",
    # ],
)