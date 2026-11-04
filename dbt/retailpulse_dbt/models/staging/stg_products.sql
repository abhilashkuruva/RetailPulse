{{ config(materialized='view') }}

with source as (
    select * from {{ source('retailpulse_raw', 'products') }}
),

renamed_and_cleaned as (
    select
        cast(product_id as int64) as product_id,
        trim(product_name) as product_name,
        trim(category) as category,
        trim(brand) as brand,
        cast(unit_price as numeric) as unit_price,
        cast(cost_price as numeric) as cost_price,
        cast(stock_quantity as int64) as stock_quantity,
        -- Calculated unit margin and markup
        round(cast(unit_price as numeric) - cast(cost_price as numeric), 2) as unit_margin,
        case
            when cast(cost_price as numeric) > 0 then
                round((cast(unit_price as numeric) - cast(cost_price as numeric)) / cast(cost_price as numeric) * 100, 2)
            else 0
        end as markup_pct,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at,
        batch_id,
        source_file,
        coalesce(ingestion_timestamp, current_timestamp()) as ingestion_timestamp
    from source
    where product_id is not null
      and cast(unit_price as numeric) >= 0
      and cast(cost_price as numeric) >= 0
)

select * from renamed_and_cleaned

