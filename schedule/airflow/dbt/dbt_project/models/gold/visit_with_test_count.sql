{{ config(
    materialized='table',
    schema='gold'
) }}

with test_agg as (

    select
        visit_id,
        count(test_id) as test_count
    from {{ source('mysql', 'health_records') }}
    where test_id is not null
    group by visit_id
)

select
    v.*,
    coalesce(t.test_count, 0) as test_count

from {{ source('postgresql', 'visits') }} v
left join test_agg t
    on v.visit_id = t.visit_id
