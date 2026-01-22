import generate # 生成graph邻接矩阵
import json # 导入json库
from a_star import * # 导入A*算法
from datetime import datetime # 导入datetime库
import streamlit as st # 导入streamlit库
import pytz # 导入pytz库
from same import * # 导入same模块
import init # 初始化

station_size = init.init_station_size()

def main():
    st.set_page_config(
        page_title="Pathfinder北京地铁路径规划系统",
        page_icon="./Pathfinder.ico",
        layout="wide"
    )

    # 初始化session_state来管理页面状态
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    # 初始化方案配置
    if 'strategy_config' not in st.session_state:
        st.session_state.strategy_config = {
            '时间优先': {'peak': 5, 'off_peak': 3},
            '综合推荐': {'peak': 10, 'off_peak': 8},
            '换乘最少': {'peak': 15, 'off_peak': 13}
        }
    
    # 初始化当前方案
    if 'current_strategy' not in st.session_state:
        st.session_state.current_strategy = '综合推荐'

    # 侧边栏导航
    with st.sidebar:
        st.title('Pathfinder北京地铁路径规划系统')
        if st.button('首页', key='home'):
            st.session_state.page = 'home'
        st.markdown('---')
        st.markdown('- [README.md](https://github.com/xhdlphzr/Pathfinder/blob/main/README.md)')
        st.markdown('- [MIT LICENSE](https://github.com/xhdlphzr/Pathfinder/blob/main/LICENSE)') 
        st.markdown('- [Github Repository](https://github.com/xhdlphzr/Pathfinder)')
        st.markdown('---')

    # 主页内容
    def home_page():
        st.title("欢迎使用Pathfinder北京地铁路径规划系统!")

        with st.expander("🗺️ 点击查看北京地铁线路图", expanded=False):
            try:
                st.image('./data/beijing_subway.png', 
                    caption='北京地铁线路图', 
                    use_container_width=True)
                st.caption("参考此图输入起点和终点站点")
            except FileNotFoundError:
                st.error("地铁线路图文件未找到, 请确认beijing_subway.png文件在data目录下")
            except Exception as e:
                st.error(f"加载图片时出现错误: {str(e)}")

        st.write("请输入起始站点和终点站点以获取推荐路线。")
        
        # 创建两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            start_name = st.text_input("起始站点名称 (无需'站'字):", key="start")
        with col2:
            end_name = st.text_input("终点站点名称 (无需'站'字):", key="end")
        
        # 时间输入
        time_col1, time_col2 = st.columns([2, 1])
        with time_col1:
            time_input = st.text_input("开始时间 (格式: HH:MM, 默认为当前时间):", value=datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%H:%M"))
        
        # 添加方案选择和换乘惩罚因子设置
        st.markdown("---")
        st.subheader("🎯 路径规划方案")
        
        # 方案选择
        strategy_col1, strategy_col2 = st.columns([1, 2])
        with strategy_col1:
            selected_strategy = st.selectbox(
                "选择规划方案",
                options=["时间优先", "综合推荐", "换乘最少", "自定义"],
                index=1,  # 默认选择"综合推荐"
                help="选择不同的路径规划策略"
            )
        
        with strategy_col2:
            if selected_strategy == "时间优先":
                st.success("⏱️ 时间优先：追求最快到达，可能包含较多换乘")
            elif selected_strategy == "综合推荐":
                st.info("⚖️ 综合推荐：平衡时间和换乘次数的最佳方案")
            elif selected_strategy == "换乘最少":
                st.warning("🔄 换乘最少：尽量减少换乘次数，时间可能稍长")
            else:
                st.info("🎛️ 自定义：手动调整换乘惩罚因子")
        
        # 更新当前方案
        if selected_strategy != st.session_state.current_strategy:
            st.session_state.current_strategy = selected_strategy
        
        st.markdown("---")
        st.subheader("🧪 换乘惩罚因子设置")
        
        # 根据选择的方案设置默认值
        if selected_strategy in st.session_state.strategy_config:
            default_peak = st.session_state.strategy_config[selected_strategy]['peak']
            default_off_peak = st.session_state.strategy_config[selected_strategy]['off_peak']
        else:
            default_peak = 10
            default_off_peak = 8
        
        # 创建两列布局用于两个滑动条
        penalty_col1, penalty_col2 = st.columns(2)
        
        with penalty_col1:
            # 如果选择预设方案，禁用滑动条；如果选择自定义，启用滑动条
            disabled = (selected_strategy != "自定义")
            peak_penalty = st.slider(
                "高峰期换乘惩罚因子 (分钟)",
                min_value=0,
                max_value=20,
                value=default_peak,
                step=1,
                disabled=disabled,
                help="高峰期每次换乘的额外时间惩罚" + (" (当前使用预设方案)" if disabled else "")
            )
            st.metric("高峰期惩罚值", f"{peak_penalty}分钟")
            
        with penalty_col2:
            off_peak_penalty = st.slider(
                "平峰期换乘惩罚因子 (分钟)", 
                min_value=0,
                max_value=20,
                value=default_off_peak,
                step=1,
                disabled=disabled,
                help="平峰期每次换乘的额外时间惩罚" + (" (当前使用预设方案)" if disabled else "")
            )
            st.metric("平峰期惩罚值", f"{off_peak_penalty}分钟")
        
        # 显示方案说明
        if selected_strategy != "自定义":
            current_config = st.session_state.strategy_config[selected_strategy]
            st.caption(f"当前方案「{selected_strategy}」: 高峰期 {current_config['peak']}分钟, 平峰期 {current_config['off_peak']}分钟")
        else:
            st.caption("自定义模式：手动调整换乘惩罚因子来影响路径规划偏好")
        
        st.markdown("---")
        
        # 加载图数据
        @st.cache_data
        def load_graph():
            graph = [[-1] * station_size for _ in range(station_size)]
            try:
                with open('./data/graph.txt', 'r', encoding='utf-8') as f:
                    for i in range(1, station_size):
                        line = f.readline().strip().split()
                        for j in range(1, station_size):
                            graph[i][j] = int(line[j - 1])
                return graph
            except FileNotFoundError:
                st.error("图数据文件未找到, 请确保graph.txt文件存在")
                return None
        
        graph = load_graph()
        
        if st.button("开始路径规划", key="a_star", type="primary"):
            if not start_name or not end_name:
                st.error("请输入起始站点和终点站点!")
                return
                
            if not time_input:
                st.error("请输入时间!")
                return
            
            # 解析时间
            try:
                hour, minute = map(int, time_input.split(':'))
                time_minutes = hour * 60 + minute
            except ValueError:
                st.error("时间格式错误, 请使用 HH:MM 格式")
                return

            # 加载站点ID映射
            @st.cache_data
            def load_id_map():
                try:
                    with open('./data/id.json', 'r', encoding='utf-8') as f:
                        return json.load(f)
                except FileNotFoundError:
                    st.error("站点ID映射文件未找到")
                    return None

            id_map = load_id_map()
            if id_map is None:
                return
            
            if start_name not in id_map:
                if same(start_name):
                    suggestion = same(start_name)[1]
                    st.warning(f"起始站点 '{start_name}' 不存在! 您是否想输入 '{suggestion}' ?")
                    return

                st.error(f"起始站点 '{start_name}' 不存在!")
                return
                
            if end_name not in id_map:
                if same(end_name):
                    suggestion = same(end_name)[1]
                    st.warning(f"终点站点 '{end_name}' 不存在! 您是否想输入 '{suggestion}' ?")
                    return

                st.error(f"终点站点 '{end_name}' 不存在!")
                return
            
            start_id = id_map[start_name]
            end_id = id_map[end_name]

            # 显示加载状态
            with st.spinner('正在计算最优路径...'):
                try:
                    new_time, use_time, path = a_star(start_id, end_id, time_minutes, graph, peak_penalty, off_peak_penalty)
                    
                    # 显示结果
                    st.success("路径规划完成！")
                    
                    # 创建结果展示区域
                    st.subheader("📋 规划结果")
                    
                    # 路径显示
                    path_text = " → ".join(path)
                    st.info(f"**推荐路线:** {path_text}")
                    
                    # 时间信息
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("预计到达时间", f"{((new_time // 60) % 24):02d}:{new_time % 60:02d}")
                    with col2:
                        st.metric("总用时", f"{use_time} 分钟")
                        
                except Exception as e:
                    st.error(f"路径规划过程中出现错误: {str(e)}")

    # 根据当前页面状态显示对应内容
    if st.session_state.page == 'home':
        home_page()

if __name__ == "__main__":
    main()