import generate # 生成graph邻接矩阵
import json # 导入json库
from a_star import * # 导入A*算法
import tkinter as tk # 导入tkinter库
from datetime import datetime # 导入datetime库

def main():
    """Pathfinder主程序 (CLI版)"""
    # 读取图的邻接矩阵
    graph = [[-1] * 402 for _ in range(402)]

    with open('./data/graph.txt', 'r', encoding='utf-8') as f:
        for i in range(1, 402):
            line = f.readline().strip().split()
            for j in range(1, 402):
                graph[i][j] = int(line[j - 1])

    print("欢迎使用Pathfinder北京地铁路径规划系统!")
    start_name = input("请输入起始站点名称: ")
    end_name = input("请输入终点站点名称: ")

    with open('./data/id.json', 'r', encoding='utf-8') as f:
        id_map = json.load(f)

    start_id = id_map[start_name]
    end_id = id_map[end_name]
    now = datetime.now()
    time_minutes = now.hour * 60 + now.minute

    new_time, use_time, path = a_star(start_id, end_id, time_minutes, graph)
    print(f"推荐路线: {' -> '.join([str(station_id) for station_id in path])}")
    print(f"预计到达时间: {new_time // 60:02d}:{new_time % 60:02d} (共用时{use_time}分钟)")

if __name__ == "__main__":
    main()