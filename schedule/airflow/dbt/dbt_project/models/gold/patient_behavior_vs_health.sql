{{ config(
    materialized='table',
    schema='gold'
) }}

-- =========================
-- DAILY BEHAVIOR (MANUAL LOG)
-- =========================
with behavior_daily as (
    select
        patient_id,
        behavior_date,

        avg(total_calories)        as avg_calories_intake,
        avg(water_intake_ml)       as avg_water_intake

    from {{ ref('daily_behavior_logs') }}
    group by
        patient_id,
        behavior_date
),

-- =========================
-- DAILY WEARABLE (SMART BAND)
-- =========================
wearable_daily as (
    select
        patient_id,
        activity_date,

        daily_steps,
        run_distance,
        calories_burned,
        standing_hours,
        sleep_hours,
        deep_sleep_hours,
        avg_heart_rate,
        avg_spo2,
        avg_stress_level
    from {{ ref('daily_smartband_record') }}
    
),

-- =========================
-- HEALTH STATIC METRICS
-- =========================
health_agg as (
    select
        patient_id,
        avg(bmi)                   as avg_bmi
    from {{ source('mysql', 'health_records') }}
    group by patient_id
)

-- =========================
-- FINAL DAILY GOLD
-- =========================
select
    p.patient_id,
    d.activity_date,

    p.age_group,
    p.gender,

    -- behavior
    b.avg_calories_intake,
    b.avg_water_intake,

    -- wearable (daily)
    d.daily_steps,
    d.run_distance,
    d.calories_burned,
    d.standing_hours,
    d.sleep_hours,
    d.deep_sleep_hours,
    d.avg_heart_rate,
    d.avg_spo2,
    d.avg_stress_level,

    -- health
    h.avg_bmi

from {{ ref('daily_smartband_record') }} d

left join {{ ref('patient_overview_core') }} p
    on p.patient_id = d.patient_id

left join health_agg h
    on p.patient_id = h.patient_id

left join behavior_daily b
    on p.patient_id = b.patient_id
   and d.activity_date = b.behavior_date


