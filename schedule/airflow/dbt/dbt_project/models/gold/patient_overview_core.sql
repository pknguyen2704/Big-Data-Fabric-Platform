{{ config(
    materialized='table',
    schema='gold'
) }}

with visits_agg as (
    select
        patient_id,
        count(distinct visit_id)           as visit_count_per_patient,
        max(visit_date)                    as last_visit_date
    from {{ source('postgresql', 'visits') }}
    group by patient_id
),

health_agg as (
    select
        patient_id,
        avg(bmi)                           as avg_bmi,

        -- max snapshot comorbidity count per patient

        max(
            case
                when comorbidities_snapshot is null
                     or trim(comorbidities_snapshot) in ('', 'None')
                then 0
                else cardinality(
                    split(comorbidities_snapshot, ',')
                )
            end
        )                                  as comorbidity_count

    from {{ source('mysql', 'health_records') }}
    group by patient_id
)

select
    p.patient_id,
    p.fullname,
    p.gender,
    p.age,

    case
        when p.age < 18 then 'Dưới 18'
        when p.age between 18 and 35 then '18-35'
        when p.age between 36 and 60 then '36-60'
        else 'Trên 60'
    end                                    as age_group,
    p.ethnicity,
    p.city,
    p.district,
    p.job, 
    
    -- visit metrics
    v.visit_count_per_patient,
    v.last_visit_date,

    -- health metrics
    h.avg_bmi,
    case
        when h.avg_bmi < 18.5 then 'Gầy'
        when h.avg_bmi < 25 then 'Bình thường'
        when h.avg_bmi < 30 then 'Thừa cân'
        else 'Béo phì'
    end                                    as bmi_category,

    h.comorbidity_count

from {{ source('snowflake', 'info') }} p
left join visits_agg v
    on p.patient_id = v.patient_id
left join health_agg h
    on p.patient_id = h.patient_id
