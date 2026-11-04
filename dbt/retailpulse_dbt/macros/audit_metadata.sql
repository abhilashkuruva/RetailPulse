{% macro audit_metadata() %}
    current_timestamp() as dbt_updated_at,
    '{{ invocation_id }}' as dbt_invocation_id
{% endmacro %}

