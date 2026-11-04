{{
    config(
        materialized='table',
        partition_by={
            "field": "sale_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["shipping_city", "payment_method"]
    )
}}

with orders as (
    select * from {{ ref('fct_orders') }}
)

select
    order_date_day as sale_date,
    shipping_city,
    shipping_state,
    payment_method,
    count(distinct order_id) as total_orders,
    count(distinct case when is_delivered then order_id end) as delivered_orders,
    count(distinct case when is_cancelled_or_returned then order_id end) as cancelled_orders,
    count(distinct customer_id) as unique_customers,
    round(sum(case when not is_cancelled_or_returned then total_amount else 0 end), 2) as net_revenue,
    round(sum(order_gross_amount), 2) as gross_revenue,
    round(sum(order_discount_amount), 2) as total_discounts,
    round(avg(case when not is_cancelled_or_returned then total_amount else null end), 2) as average_order_value
from orders
group by 1, 2, 3, 4

