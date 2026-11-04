{{
    config(
        materialized='table',
        partition_by={
            "field": "transaction_date_day",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["order_id", "payment_status"]
    )
}}

with payments as (
    select * from {{ ref('stg_payments') }}
),

orders as (
    select order_id, customer_id, shipping_city, shipping_state
    from {{ ref('stg_orders') }}
)

select
    p.payment_id,
    p.order_id,
    o.customer_id,
    p.payment_method,
    p.payment_amount,
    p.payment_status,
    p.is_successful_payment,
    p.transaction_date,
    p.transaction_date_day,
    o.shipping_city,
    o.shipping_state,
    p.updated_at
from payments p
left join orders o
    on p.order_id = o.order_id

