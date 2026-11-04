{% snapshot snap_products %}

{{
    config(
      target_schema=env_var('BIGQUERY_STAGING_DATASET', 'retailpulse_staging'),
      unique_key='product_id',
      strategy='check',
      check_cols=['unit_price', 'cost_price', 'category'],
      invalidate_hard_deletes=True
    )
}}

select
    product_id,
    product_name,
    category,
    brand,
    unit_price,
    cost_price,
    stock_quantity,
    updated_at
from {{ source('retailpulse_raw', 'products') }}

{% endsnapshot %}

