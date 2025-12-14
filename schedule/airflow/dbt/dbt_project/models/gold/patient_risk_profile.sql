{{ config(
    materialized='table',
    schema='gold'
) }}

with wearable_agg as (
    select
        patient_id,
        avg(heart_rate)                    as avg_heart_rate,
        avg(stress_level)                  as avg_stress_level,
        avg(
            (deep_sleep_hours / nullif(sleep_hours, 0)) * 100
        )                                  as avg_sleep_quality_index
    from {{ ref('smart_band') }}
    where patient_id is not null
    group by patient_id
)

select
    p.patient_id,
    p.fullname,
    p.gender,
    p.age,
    p.age_group,
    p.city,

    p.visit_count_per_patient,
    p.avg_bmi,
    p.bmi_category,
    p.comorbidity_count,

    w.avg_heart_rate,
    w.avg_stress_level,
    w.avg_sleep_quality_index,

    least(
        100,
        (p.age / 10)
        + (case
              when p.bmi_category = 'Béo phì' then 20
              when p.bmi_category = 'Thừa cân' then 10
              else 0
          end)
        + (p.comorbidity_count * 5)
        + (p.visit_count_per_patient * 2)
        + (coalesce(w.avg_stress_level, 0) * 5)
    )                                     as overall_risk_score

from {{ ref('patient_overview_core') }} p
left join wearable_agg w
    on p.patient_id = w.patient_id
