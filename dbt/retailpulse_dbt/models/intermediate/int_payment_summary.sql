{{ config(materialized='view') }}

with payments as (
    select * from {{ ref('stg_payments') }}
),

payment_rollups as (
    select
        order_id,
        count(payment_id) as total_payment_attempts,
        sum(case when is_successful_payment then 1 else 0 end) as successful_payment_count,
        round(sum(case when is_successful_payment then payment_amount else 0 end), 2) as total_amount_paid,
        max(transaction_date) as latest_payment_timestamp,
        -- Primary payment instrument used
        array_agg(payment_method order by transaction_date desc)[offset(0)] as primary_payment_method,
        -- Overall payment settlement status
        case
            when sum(case when is_successful_payment then 1 else 0 end) > 0 then 'settled'
            when sum(case when payment_status = 'pending' then 1 else 0 end) > 0 then 'pending'
            else 'failed'
        end as order_payment_status
    from payments
    group by 1
)

select * from payment_rollups

