-- Singular Data Quality Test: assert_no_negative_product_prices.sql
-- Fails if any product has a negative unit price or negative cost price.

select
    product_id,
    product_name,
    unit_price,
    cost_price
from {{ ref('dim_products') }}
where unit_price < 0
   or cost_price < 0

