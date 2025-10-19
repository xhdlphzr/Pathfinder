import json
import heapq
from geopy.distance import distance

def a_star(start, end, time, graph):
    """
    A*算法实现北京路径规划问题
    变量说明:
    start: 起始站点id
    end: 终点站点id 
    time: 从现在到当天0:00的分钟数
    graph: 图的邻接矩阵表示, graph[i][j]表示i到j的距离, -1表示不连通
    """

    # 根据时间判断当前速度
    def now_speed(time):
        if (420 <= time < 540) or (1020 <= time < 1140):
            return 35000 # 高峰期速度35000m/h
        else:
            return 45000 # 平峰期速度45000m/h
        
    def now_punishment(time):
        if (420 <= time < 540) or (1020 <= time < 1140):
            return 5 # 高峰期换乘惩罚因子5
        else:
            return 3 # 平峰期换乘惩罚因子3
    
    with open('./data/station.json', 'r', encoding='utf-8') as f:
        station_data = json.load(f)

    # 启发式函数
    def heuristic(idx1, idx2):
        coord1 = (station_data[str(idx1)]['纬度'], station_data[str(idx1)]['经度'])
        coord2 = (station_data[str(idx2)]['纬度'], station_data[str(idx2)]['经度'])
        dis = distance(coord1, coord2).m

        speed = 40000 # 这里因为是估算函数, 所以估个40000m/h的速度
        return round(dis / speed * 60) # 返回分钟

    # 是否换乘
    def is_transfer(idx_prev, idx_now, idx_next):
        if idx_prev == -1 or idx_next == -1:
            return False

        lines_prev = set(station_data[str(idx_prev)]['线路'])
        lines_now = set(station_data[str(idx_now)]['线路'])
        lines_next = set(station_data[str(idx_next)]['线路'])
        
        if lines_prev & lines_now != lines_now & lines_next:
            return True
        else:
            return False
        
    # 初始化数据结构
    open_list = []
    heapq.heappush(open_list, (heuristic(start, end), heuristic(start, end), start)) # (f, h, id)
    close_list = []
    prev = [-1] * 402
    g = [999999999] * 402 # 到这个点的最优时间到当天0:00的分钟数
    g[start] = time

    while open_list:
        f, h, now = heapq.heappop(open_list)

        # 最优性剪枝
        if f > g[now] + heuristic(now, end):
            continue

        # 可行性剪枝
        if now in close_list:
            continue

        close_list.append(now)

        # 因为我用的启发式函数是<=实际值的, 所以第一个到达终点的就是最优解
        if now == end:
            path = []
            ans = now

            while ans != -1:
                path.append(station_data[str(ans)]['站点'])
                ans = prev[ans]
            path.reverse()

            return g[end], g[end] - time, path

        for neighbor in range(1, 402):
            # 有连接
            if graph[now][neighbor] != -1:
                # 更新graph值
                now_time = round(graph[now][neighbor] / now_speed(g[now]) * 60)

                if is_transfer(prev[now], now, neighbor):
                    now_time += now_punishment(g[now])
                
                if g[neighbor] != 999999999:
                    if g[neighbor] > g[now] + now_time:
                        g[neighbor] = g[now] + now_time
                        heapq.heappush(open_list, (g[neighbor] + heuristic(neighbor, end), heuristic(neighbor, end), neighbor)) # 空间占用大, 时间不变
                        prev[neighbor] = now
                else:
                    g[neighbor] = g[now] + now_time
                    heapq.heappush(open_list, (g[neighbor] + heuristic(neighbor, end), heuristic(neighbor, end), neighbor)) # 空间占用大, 时间不变
                    prev[neighbor] = now