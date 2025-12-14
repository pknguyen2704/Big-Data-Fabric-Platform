{{ config(
    materialized='table',
    schema='gold'
) }}

select
        patient_id,
        device_id,
        activity_date,

        -- cumulative metrics → MAX
        max(daily_steps)           as daily_steps,
        max(run_distance)          as run_distance,
        max(calories_burned)       as calories_burned,
        max(standing_hours)        as standing_hours,
        max(sleep_hours)           as sleep_hours,
        max(deep_sleep_hours)      as deep_sleep_hours,

        -- snapshot metrics → AVG
        avg(heart_rate)            as avg_heart_rate,
        avg(spo2)                  as avg_spo2,
        -- stress: AVG + ROUND
        cast(round(avg(stress_level)) as integer)
                                 as avg_stress_level

    from {{ ref('smart_band') }}
    group by
        patient_id,
        device_id,
        activity_date