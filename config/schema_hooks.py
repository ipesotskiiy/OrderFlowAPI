def enforce_non_empty_order_items(
    result,
    generator,
    request,
    public,
):
    for schema_name in ("OrderCreate", "OrderUpdate", "PatchedOrderUpdate"):
        result["components"]["schemas"][schema_name]["properties"]["order_items"]["minItems"] = 1
    return result
