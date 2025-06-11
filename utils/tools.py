import aiohttp
import re


async def format_referrals_list(data, paginate_index):
    data_paginate = []

    num_pages = (len(data) // paginate_index) + (1 if len(data) % paginate_index > 0 else 0)
    for j in range(num_pages):
        page_data = []
        for i in range(paginate_index):
            index = i + (j * paginate_index)
            if index < len(data):
                item = data[index]
                string = f"{index + 1}. @{item['username']} - {item['join_date']}"
                page_data.append(string)
        data_paginate.append(page_data)

    return data_paginate


async def is_contain_link(text):
    url_pattern = re.compile(
 r'(?:(?:https?|ftp)://)'
        r'|(?:www\.)'
        r'|(?:[a-z0-9-]+\.)'
        r'[^\s/$.?#].[^\s]*',
        re.IGNORECASE
    )

    return bool(url_pattern.search(text))
