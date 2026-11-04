-- Singular Data Quality Test: assert_order_total_matches_items.sql
-- Fails if any order's recorded net total deviates from the sum of its order line-items by > 0.05 currency units.

with order_sums as (
    select
        order_id,
        round(sum(net_amount), 2) as calculated_sum
    from {{ ref('stg_order_items') }}
    group by 1
),

validation as (
    select
        o.order_id,
        o.total_amount,
        s.calculated_sum,
        abs(o.total_amount - s.calculated_sum) as variance
    from {{ ref('fct_orders') }} o
    join order_sums s
        on o.order_id = s.order_id
    where abs(o.total_amount - s.calculated_sum) > 0.05
)

select * from validation

