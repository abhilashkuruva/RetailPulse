{{ config(materialized='view') }}

with source as (
    select * from {{ source('retailpulse_raw', 'order_items') }}
),

renamed_and_cleaned as (
    select
        cast(order_item_id as int64) as order_item_id,
        cast(order_id as int64) as order_id,
        cast(product_id as int64) as product_id,
        cast(quantity as int64) as quantity,
        cast(unit_price as numeric) as unit_price,
        cast(discount_amount as numeric) as discount_amount,
        -- Gross item value before discount
        round(cast(quantity as numeric) * cast(unit_price as numeric), 2) as gross_amount,
        -- Net line amount after discount
        round((cast(quantity as numeric) * cast(unit_price as numeric)) - cast(discount_amount as numeric), 2) as net_amount,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at,
        batch_id,
        source_file,
        coalesce(ingestion_timestamp, current_timestamp()) as ingestion_timestamp
    from source
    where order_item_id is not null
      and order_id is not null
      and product_id is not null
      and cast(quantity as int64) > 0
      and cast(unit_price as numeric) >= 0
)

select * from renamed_and_cleaned
