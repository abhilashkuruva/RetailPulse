{{ config(materialized='table', cluster_by=["customer_loyalty_segment", "customer_value_tier"]) }}

with customers as (
    select * from {{ ref('dim_customers') }}
)

select
    customer_id,
    full_name,
    email,
    city,
    state,
    registration_date,
    lifetime_orders,
    lifetime_delivered_orders,
    lifetime_cancelled_orders,
    first_order_timestamp,
    most_recent_order_timestamp,
    -- Recency: Days elapsed since most recent order
    date_diff(current_date(), date(most_recent_order_timestamp), day) as days_since_last_order,
    lifetime_spend,
    avg_order_spend,
    customer_loyalty_segment,
    customer_value_tier,
    -- RFM Category Heuristic
    case
        when lifetime_spend > 20000 and date_diff(current_date(), date(most_recent_order_timestamp), day) <= 60 then 'Champion'
        when lifetime_spend > 10000 and date_diff(current_date(), date(most_recent_order_timestamp), day) <= 90 then 'Loyal Customer'
        when lifetime_spend > 5000 and date_diff(current_date(), date(most_recent_order_timestamp), day) > 180 then 'At Risk'
        when lifetime_orders = 1 and date_diff(current_date(), date(most_recent_order_timestamp), day) <= 30 then 'New Active'
        else 'Standard Retained'
    end as rfm_persona
from customers

