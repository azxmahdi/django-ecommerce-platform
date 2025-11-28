def build_pagination_items(context_data):
    if context_data.get("is_paginated"):
        p, page = context_data["paginator"], context_data["page_obj"]
        nums = {1, p.num_pages, page.number - 1, page.number, page.number + 1}
        nums = sorted(n for n in nums if 1 <= n <= p.num_pages)
        items, prev = [], None
        for n in nums:
            if prev and n - prev > 1:
                items.append({"ellipsis": True})
            items.append({"number": n})
            prev = n
        return items
    return []
