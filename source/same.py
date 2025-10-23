import json
import heapq

def same(x):
    """
    搜索类似的站点名称
    变量说明:
    x: 输入的站点的名称
    """

    with open('./data/id.json', 'r', encoding='utf-8') as f:
        id_map = json.load(f)

    results = []

    for i in id_map.keys():
        if (set(x) & set(i)).__len__() > 0:
            heapq.heappush(results, (-((set(x) & set(i)).__len__()), i))

    ans = heapq.heappop(results) if results else None
    return ans if ans else None