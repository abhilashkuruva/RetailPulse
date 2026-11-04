{{ config(materialized='view') }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

item_aggregates as (
    select
        order_id,
        count(order_item_id) as total_line_items,
        sum(quantity) as total_units_ordered,
        round(sum(gross_amount), 2) as order_gross_amount,
        round(sum(discount_amount), 2) as order_discount_amount,
        round(sum(net_amount), 2) as order_net_amount
    from order_items
    group by 1
),

enriched_orders as (
    select
        o.order_id,
        o.customer_id,
        o.order_date,
        o.order_date_day,
        o.order_status,
        o.payment_method,
        o.shipping_city,
        o.shipping_state,
        o.is_delivered,
        o.is_cancelled_or_returned,
        coalesce(ia.total_line_items, 0) as total_line_items,
        coalesce(ia.total_units_ordered, 0) as total_units_ordered,
        coalesce(ia.order_gross_amount, 0.0) as order_gross_amount,
        coalesce(ia.order_discount_amount, 0.0) as order_discount_amount,
        coalesce(ia.order_net_amount, 0.0) as order_net_amount,
        o.updated_at
    from orders o
    left join item_aggregates ia
        on o.order_id = ia.order_id
)

select * from enriched_orders

