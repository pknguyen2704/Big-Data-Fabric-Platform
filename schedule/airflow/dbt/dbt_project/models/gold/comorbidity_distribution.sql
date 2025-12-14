{{ config(
    materialized='table',
    schema='gold'
) }}

with exploded as (

    select
        patient_id,
        trim(comorbidity) as comorbidity
    from {{ source('mysql', 'health_records') }},
         unnest(split(comorbidities_snapshot, ',')) as t(comorbidity)

),

deduplicated as (

    select distinct
        patient_id,
        comorbidity
    from exploded
    where comorbidity is not null
)

select
    comorbidity,
    count(patient_id)                                   as patient_count,
    round(
        count(patient_id) * 100.0
        / sum(count(patient_id)) over (),
        2
    )                                                   as percentage
from deduplicated
group by comorbidity
order by patient_count desc
