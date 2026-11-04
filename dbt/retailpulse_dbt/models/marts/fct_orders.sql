{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        partition_by={
            "field": "order_date_day",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["customer_id", "order_status"]
    )
}}

with order_details as (
    select * from {{ ref('int_order_details') }}
),

payment_summary as (
    select * from {{ ref('int_payment_summary') }}
),

final as (
    select
        od.order_id,
        od.customer_id,
        od.order_date,
        od.order_date_day,
        od.order_status,
        od.payment_method,
        od.shipping_city,
        od.shipping_state,
        od.is_delivered,
        od.is_cancelled_or_returned,
        od.total_line_items,
        od.total_units_ordered,
        od.order_gross_amount,
        od.order_discount_amount,
        od.order_net_amount as total_amount,
        coalesce(ps.total_amount_paid, 0.0) as amount_paid,
        coalesce(ps.order_payment_status, 'unpaid') as payment_status,
        od.updated_at
    from order_details od
    left join payment_summary ps
        on od.order_id = ps.order_id
)

select * from final

{% if is_incremental() %}
  -- Incremental processing filter:
  -- Only scan and merge records whose updated_at timestamp is newer than the max updated_at
  -- currently existing in the target table, minus a 3-day lookback window for late-arriving data
  where updated_at >= (
      select timestamp_sub(coalesce(max(updated_at), timestamp('1970-01-01')), interval 3 day)
      from {{ this }}
  )
{% endif %}
