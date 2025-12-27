import json
from geopy.distance import distance

def generate_graph():
    """生成地铁线路的邻接矩阵"""
    # 读取数据
    with(open('./data/line.json', 'r', encoding='utf-8')) as f:
        line = json.load(f)

    with(open('./data/station.json', 'r', encoding='utf-8')) as f:
        station = json.load(f)

    with(open('./data/id.json', 'r', encoding='utf-8')) as f:
        id_map = json.load(f)

    graph = [[-1] * 411 for _ in range(411)] # 邻接矩阵
    for i in range(1, 411):
        graph[i][i] = 0

    for i in line:
        for station_id, station_info in line[i].items():
            name_now = station_info['站点']
            name_prev = station_info['前一站']
            name_next = station_info['后一站']

            if name_prev is not None:
                graph[id_map[name_now]][id_map[name_prev]] = round(distance(
                    (station[str(id_map[name_now])]['纬度'], station[str(id_map[name_now])]['经度']),
                    (station[str(id_map[name_prev])]['纬度'], station[str(id_map[name_prev])]['经度'])
                ).m)
                graph[id_map[name_prev]][id_map[name_now]] = graph[id_map[name_now]][id_map[name_prev]]

            if name_next is not None:
                graph[id_map[name_now]][id_map[name_next]] = round(distance(
                    (station[str(id_map[name_now])]['纬度'], station[str(id_map[name_now])]['经度']),
                    (station[str(id_map[name_next])]['纬度'], station[str(id_map[name_next])]['经度'])
                ).m)
                graph[id_map[name_next]][id_map[name_now]] = graph[id_map[name_now]][id_map[name_next]]

    with(open('./data/graph.txt', 'w', encoding='utf-8')) as f:
        for i in range(1, 411):
            for j in range(1, 411):
                print(graph[i][j], end=' ', file=f)
            print('', file=f)

generate_graph()