{{ config(
    materialized='table'
) }}

with cleaned as (

    select
        -- ===== KEYS =====
        device_id,
        patient_id,
        -- ===== ACTIVITY =====
        case
            when daily_steps >= 0 then daily_steps
            else null
        end                                                     as daily_steps,

        case
            when spo2 between 70 and 100 then spo2
            else null
        end                                                     as spo2,

        -- ===== SLEEP =====
        case
            when sleep_hours >= 0 then sleep_hours
            else null
        end                                                     as sleep_hours,

        case
            when deep_sleep_hours >= 0
                 and sleep_hours is not null
                 and deep_sleep_hours <= sleep_hours
                then deep_sleep_hours
            else null
        end                                                     as deep_sleep_hours,

        -- ===== ENERGY =====
        case
            when calories_burned >= 0 then calories_burned
            else null
        end                                                     as calories_burned,

        -- ===== POSTURE / MOVEMENT =====
        case
            when standing_hours between 0 and 24
                then standing_hours
            else null
        end                                                     as standing_hours,

        case
            when run_distance >= 0 then run_distance
            else null
        end                                                     as run_distance,

        -- ===== STRESS =====
        case
            when stress_level in (1, 2, 3)
                then stress_level
            else null
        end                                                     as stress_level,

        -- ===== HEART =====
        case
            when heart_rate between 30 and 220
                then heart_rate
            else null
        end                                                     as heart_rate,

        -- ===== TIME =====
        from_unixtime(created_at / 1000)                        as created_at,
        cast(from_unixtime(created_at / 1000) as date)          as activity_date

    from {{ source('kafka', 'smart_band') }}
    where device_id is not null
)

select *
from cleaned
where
    daily_steps       is not null
    and spo2          is not null
    and sleep_hours   is not null
    and deep_sleep_hours is not null
    and calories_burned  is not null
    and standing_hours   is not null
    and run_distance     is not null
    and stress_level     is not null
    and heart_rate       is not null

