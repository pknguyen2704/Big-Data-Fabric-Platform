{{ config(
    materialized='table'
) }}

select
    -- ===== KEYS =====
    trim(patient_id)                                   as patient_id,

    -- ===== DATE =====
    cast(date as date)                                 as behavior_date,

    -- ===== DIET =====
    nullif(trim(diet.breakfast), '')                   as breakfast,
    nullif(trim(diet.lunch), '')                       as lunch,
    nullif(trim(diet.dinner), '')                      as dinner,
    nullif(trim(diet.snack), '')                       as snack,

    coalesce(diet.total_calories, 0)                   as total_calories,

    -- ===== EXERCISE =====
    nullif(trim(exercise.type), '')                    as exercise_type,

    coalesce(exercise.duration_hours, 0.0)             as exercise_duration_hours,

    case
        when lower(trim(exercise.intensity)) in ('low', 'nhẹ') then 'nhẹ'
        when lower(trim(exercise.intensity)) in ('medium', 'vừa') then 'vừa'
        when lower(trim(exercise.intensity)) in ('high', 'cao', 'nặng') then 'nặng'
        else null
    end                                                 as exercise_intensity,

    coalesce(exercise.calories_burned, 0.0)             as calories_burned,

    -- ===== MOOD =====
    nullif(trim(mood), '')                              as mood,

    -- ===== WATER =====
    coalesce(water_intake_ml, 0)                        as water_intake_ml,
    
    -- ===== CONTEXT (NEW) =====
    nullif(trim(context.weather), '')                       as weather,
    nullif(trim(context.location), '')                      as location,
    nullif(trim(context.special_events), '')                as special_events

from {{ source('mongodb', 'daily_behavior_logs') }}

where
    patient_id is not null
    and trim(patient_id) <> ''
