{{ config(materialized='view') }}

with source as (
    select * from {{ source('retailpulse_raw', 'orders') }}
),

renamed_and_cleaned as (
    select
        cast(order_id as int64) as order_id,
        cast(customer_id as int64) as customer_id,
        cast(order_date as timestamp) as order_date,
        date(cast(order_date as timestamp)) as order_date_day,
        lower(trim(order_status)) as order_status,
        upper(trim(payment_method)) as payment_method,
        trim(shipping_city) as shipping_city,
        trim(shipping_state) as shipping_state,
        case
            when lower(trim(order_status)) = 'delivered' then true
            else false
        end as is_delivered,
        case
            when lower(trim(order_status)) in ('cancelled', 'returned') then true
            else false
        end as is_cancelled_or_returned,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at,
        batch_id,
        source_file,
        coalesce(ingestion_timestamp, current_timestamp()) as ingestion_timestamp
    from source
    where order_id is not null
      and customer_id is not null
)

select * from renamed_and_cleaned
