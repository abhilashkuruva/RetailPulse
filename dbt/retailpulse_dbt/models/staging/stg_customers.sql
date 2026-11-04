{{ config(materialized='view') }}

with source as (
    select * from {{ source('retailpulse_raw', 'customers') }}
),

renamed_and_cleaned as (
    select
        cast(customer_id as int64) as customer_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        concat(trim(first_name), ' ', trim(last_name)) as full_name,
        lower(trim(email)) as email,
        trim(phone) as phone,
        trim(city) as city,
        trim(state) as state,
        coalesce(trim(country), 'India') as country,
        cast(registration_date as date) as registration_date,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at,
        batch_id,
        source_file,
        coalesce(ingestion_timestamp, current_timestamp()) as ingestion_timestamp
    from source
    where customer_id is not null
)

select * from renamed_and_cleaned

