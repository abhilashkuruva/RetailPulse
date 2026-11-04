{{ config(materialized='table') }}

with daily_sales as (
    select * from {{ ref('mart_daily_sales') }}
),

monthly_aggregates as (
    select
        date_trunc(sale_date, month) as sale_month,
        sum(total_orders) as total_orders,
        sum(delivered_orders) as delivered_orders,
        sum(cancelled_orders) as cancelled_orders,
        sum(net_revenue) as net_revenue,
        sum(gross_revenue) as gross_revenue,
        sum(total_discounts) as total_discounts
    from daily_sales
    group by 1
)

select
    sale_month,
    total_orders,
    delivered_orders,
    cancelled_orders,
    net_revenue,
    gross_revenue,
    total_discounts,
    round(net_revenue / nullif(total_orders, 0), 2) as monthly_aov,
    lag(net_revenue, 1) over (order by sale_month) as previous_month_revenue,
    round(
        (net_revenue - lag(net_revenue, 1) over (order by sale_month))
        / nullif(lag(net_revenue, 1) over (order by sale_month), 0) * 100, 2
    ) as mom_growth_rate_pct
from monthly_aggregates
order by sale_month asc

