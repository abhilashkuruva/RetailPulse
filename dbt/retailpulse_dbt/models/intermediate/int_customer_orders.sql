{{ config(materialized='view') }}

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

order_details as (
    select * from {{ ref('int_order_details') }}
),

customer_aggregations as (
    select
        customer_id,
        count(order_id) as lifetime_orders,
        count(case when is_delivered then order_id end) as lifetime_delivered_orders,
        count(case when is_cancelled_or_returned then order_id end) as lifetime_cancelled_orders,
        min(order_date) as first_order_timestamp,
        max(order_date) as most_recent_order_timestamp,
        round(sum(case when not is_cancelled_or_returned then order_net_amount else 0 end), 2) as lifetime_spend,
        round(avg(case when not is_cancelled_or_returned then order_net_amount else null end), 2) as avg_order_spend
    from order_details
    group by 1
),

customer_summary as (
    select
        c.customer_id,
        c.full_name,
        c.email,
        c.phone,
        c.city,
        c.state,
        c.country,
        c.registration_date,
        coalesce(ca.lifetime_orders, 0) as lifetime_orders,
        coalesce(ca.lifetime_delivered_orders, 0) as lifetime_delivered_orders,
        coalesce(ca.lifetime_cancelled_orders, 0) as lifetime_cancelled_orders,
        ca.first_order_timestamp,
        ca.most_recent_order_timestamp,
        coalesce(ca.lifetime_spend, 0.0) as lifetime_spend,
        coalesce(ca.avg_order_spend, 0.0) as avg_order_spend,
        case
            when coalesce(ca.lifetime_orders, 0) = 0 then 'Inactive/Registered Only'
            when ca.lifetime_orders = 1 then 'One-Time Buyer'
            when ca.lifetime_orders between 2 and 4 then 'Repeat Customer'
            else 'Loyal Power Shopper'
        end as customer_loyalty_segment,
        c.updated_at
    from customers c
    left join customer_aggregations ca
        on c.customer_id = ca.customer_id
)

select * from customer_summary

