{{ config(materialized='table', cluster_by=["category", "brand"]) }}

with products as (
    select * from {{ ref('stg_products') }}
)

select
    product_id,
    product_name,
    category,
    brand,
    unit_price,
    cost_price,
    unit_margin,
    markup_pct,
    stock_quantity,
    case
        when stock_quantity = 0 then 'Out of Stock'
        when stock_quantity < 50 then 'Low Stock Alert'
        else 'Healthy Inventory'
    end as inventory_health_status,
    updated_at
from products

