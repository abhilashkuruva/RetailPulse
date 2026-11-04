{{ config(materialized='view') }}

with source as (
    select * from {{ source('retailpulse_raw', 'payments') }}
),

renamed_and_cleaned as (
    select
        cast(payment_id as int64) as payment_id,
        cast(order_id as int64) as order_id,
        upper(trim(payment_method)) as payment_method,
        cast(payment_amount as numeric) as payment_amount,
        lower(trim(payment_status)) as payment_status,
        cast(transaction_date as timestamp) as transaction_date,
        date(cast(transaction_date as timestamp)) as transaction_date_day,
        case
            when lower(trim(payment_status)) = 'success' then true
            else false
        end as is_successful_payment,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at,
        batch_id,
        source_file,
        coalesce(ingestion_timestamp, current_timestamp()) as ingestion_timestamp
    from source
    where payment_id is not null
      and order_id is not null
      and cast(payment_amount as numeric) >= 0
)

select * from renamed_and_cleaned

