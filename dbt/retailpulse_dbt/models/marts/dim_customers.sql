{{ config(materialized='table', cluster_by=["city", "customer_loyalty_segment"]) }}

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
)

select
    customer_id,
    full_name,
    email,
    phone,
    city,
    state,
    country,
    registration_date,
    lifetime_orders,
    lifetime_delivered_orders,
    lifetime_cancelled_orders,
    first_order_timestamp,
    most_recent_order_timestamp,
    lifetime_spend,
    avg_order_spend,
    customer_loyalty_segment,
    case
        when lifetime_orders >= 5 and lifetime_spend >= 25000 then 'Platinum Tier'
        when lifetime_orders >= 2 and lifetime_spend >= 10000 then 'Gold Tier'
        when lifetime_orders >= 1 then 'Silver Tier'
        else 'Prospect'
    end as customer_value_tier,
    updated_at
from customer_orders

