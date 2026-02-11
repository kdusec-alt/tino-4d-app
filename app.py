import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 1. 系統初始化與頁面配置 ---
st.set_page_config(
    page_title="Tino Lucky Ball", 
    page_icon="🎱", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化 Session State (確保動畫與結果狀態持久化)
if 'screenshot_mode' not in st.session_state:
    st.session_state['screenshot_mode'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None
if 'u_name' not in st.session_state:
    st.session_state['u_name'] = ""

# --- 2. 完整 CSS 渲染引擎 (包含 iPhone 響應式佈局) ---
st.markdown("""
<style>
    /* 全局 Cyberpunk 風格 */
    .stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; max-width: 500px !important; }

    /* 拉霸機外殼佈局 */
    .slot-machine-casing {
        background: linear-gradient(135deg, #222 0%, #0d0d0d 100%);
        border: 4px solid #ffd700;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.3), inset 0 0 50px #000;
        margin-bottom: 20px;
        position: relative;
    }
    
    /* 頂部霓虹燈標題 */
    .machine-top {
        text-align: center;
        background: #4a0000;
        border-radius: 12px;
        padding: 15px 5px;
        margin-bottom: 15px;
        border: 2px solid #ff3333;
        box-shadow: 0 0 15px #ff0000, inset 0 0 20px #000;
    }
    .machine-title {
        color: #ffeb3b; font-weight: 900; font-size: 8vw; letter-spacing: 2px;
        text-shadow: 0 0 10px #ff0000; margin: 0; font-style: italic; white-space: nowrap;
    }

    /* 捲軸視窗樣式 */
    .reel-window {
        background: #000;
        border: 2px solid #333;
        border-radius: 10px;
        margin-bottom: 12px;
        padding: 10px 2px;
        box-shadow: inset 0 0 15px #000;
        position: relative;
    }
    .reel-label {
        font-size: 0.7em; color: #888; font-weight: bold; text-transform: uppercase;
        margin-bottom: 5px; text-align: center; letter-spacing: 1.5px;
    }
    .reel-label.main { color: #00e5ff; text-shadow: 0 0 5px #00e5ff; }
    .reel-label.super { color: #00ff00; text-shadow: 0 0 5px #00ff00; }
    .reel-label.scratch { color: #ffd700; text-shadow: 0 0 5px #ffd700; }

    /* 數字球動態佈局 */
    .ball-container { display: flex; justify-content: center; gap: 4px; flex-wrap: nowrap; width: 100%; }
    .ball {
        width: 8.5vw; height: 8.5vw; max-width: 36px; max-height: 36px; border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ffffff, #bbbbbb);
        color: #000; font-weight: 900; font-size: 3.8vw; max-font-size: 16px;
        display: flex; align-items: center; justify-content: center;
        border: 1.5px solid #000; box-shadow: 1px 1px 4px rgba(0,0,0,0.8); flex-shrink: 0;
    }
    .ball.special { background: radial-gradient(circle at 30% 30%, #ff3333, #990000); color: white; border: 1.5px solid #ff9999; }
    
    /* 刮刮樂文字 */
    .scratch-num { font-size: 2em; font-weight: 900; color: #ffd700; text-shadow: 0 0 12px #ff9900; letter-spacing: 12px; text-align: center; }

    /* 擬真拉桿按鈕 (The Red Lever) */
    .stButton { text-align: center; }
    div.stButton > button {
        width: 90px !important; height: 90px !important; border-radius: 50% !important;
        background: radial-gradient(circle at 30% 30%, #ff4444, #990000) !important;
        border: 4px solid #cc0000 !important;
        box-shadow: 0 8px 0 #550000, 0 15px 20px rgba(0,0,0,0.6) !important;
        color: white !important; font-weight: bold !important; font-size: 1.1em !important; margin: 15px auto !important;
    }
    div.stButton > button:active { transform: translateY(8px) !important; box-shadow: 0 0 0 #550000, inset 0 0 20px rgba(0,0,0,0.8) !important; }

    /* 狀態顯示條 */
    .status-bar { display: flex; justify-content: space-between; background: #111; border-radius: 8px; padding: 8px 15px; margin-bottom: 12px; border: 1px solid #333; }
    .status-txt { color: #fff; font-size: 0.8em; }
    .status-highlight { color: #00e5ff; font-weight: bold; margin-left: 3px; }

    /* iPhone 適配修正 */
    @media only screen and (max-width: 400px) {
        .ball { width: 7.5vw !important; height: 7.5vw !important; font-size: 3.2vw !important; }
        .machine-title { font-size: 7vw; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心演算邏輯庫 ---

def get_zodiac(year):
    """計算十二生肖"""
    zods = ["🐵", "🐔", "🐶", "🐷", "🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑"]
    return zods[year % 12]

def get_constellation(month, day):
    """計算十二星座"""
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    consts = ["♑", "♒", "♓", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐"]
    return consts[month-1] if day < dates[month-1] else consts[month]

def get_element_luck(year):
    """五行尾數定義 (Layer 1)"""
    last_digit = int(str(year)[-1])
    luck_map = {
        0: ("金", [4, 9, 0, 5]), 1: ("金", [4, 9, 0, 5]),
        2: ("水", [1, 6, 4, 9]), 3: ("水", [1, 6, 4, 9]),
        4: ("木", [3, 8, 1, 6]), 5: ("木", [3, 8, 1, 6]),
        6: ("火", [2, 7, 3, 8]), 7: ("火", [2, 7, 3, 8]),
        8: ("土", [5, 0, 2, 7]), 9: ("土", [5, 0, 2, 7])
    }
    return luck_map.get(last_digit, ("未知", []))

def check_filters(numbers):
    """第三層：反人性過濾邏輯"""
    # 1. 避開熱門生日號 (1-31 不可超過 4 顆)
    if sum(1 for n in numbers if n <= 31) > 4: return False
    # 2. 避開規律連號 (不可超過 2 組)
    sn = sorted(numbers)
    if sum(1 for i in range(len(sn)-1) if sn[i+1] == sn[i]+1) > 2: return False
    # 3. 避開純小號區
    if all(n < 25 for n in sn): return False
    # 4. 避開等差數列
    if len(set([sn[i+1]-sn[i] for i in range(len(sn)-1)])) == 1: return False
    return True

def generate_tino_numbers(lucky_digits, seed, pool_range=49):
    """三層架構選號引擎"""
    random.seed(seed)
    for _ in range(200): # 增加嘗試次數確保通過過濾
        # Layer 1: 五行尾數隨機取 2 顆 (不超過 2 顆以維持隨機分布)
        l1_pool = [n for n in range(1, pool_range+1) if n % 10 in lucky_digits]
        l1_nums = random.sample(l1_pool, 2)
        # Layer 2: 剩餘號碼純隨機補滿 4 顆
        l2_pool = [n for n in range(1, pool_range+1) if n not in l1_nums]
        l2_nums = random.sample(l2_pool, 4)
        final = l1_nums + l2_nums
        # Layer 3: 執行博弈過濾
        if check_filters(final): return sorted(final)
    return sorted(final)

def run_quantum_simulation(name, dob, audit_list):
    """量子模擬主程序"""
    elem, lucky = get_element_luck(dob.year)
    # 利用微秒級時間戳與使用者身分產生唯一 Seed
    seed = int(hashlib.sha256(f"{name}{dob}{datetime.now().strftime('%f')}".encode()).hexdigest(), 16)
    
    # 大樂透邏輯
    l_main = generate_tino_numbers(lucky, seed)
    random.seed(seed + 7) # 偏移擾動
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    # 威力彩邏輯 (第一區 38 號)
    s_main = generate_tino_numbers(lucky, seed + 88, 38)
    s_spec = random.randint(1, 8)
    
    # 刮刮樂邏輯 (嚴格遵守 2 五行 + 1 隨機)
    t_pool = [n for n in range(10) if n in lucky]
    t_nums = random.sample(t_pool, 2) + [random.randint(0,9)]
    random.shuffle(t_nums)
    
    # 雷達圖數據
    elements = ['金', '木', '水', '火', '土']
    r_vals = [random.randint(35, 65) for _ in range(5)]
    if elem in elements: r_vals[elements.index(elem)] = random.randint(88, 98)
    
    return {
        'l': l_main, 'ls': l_spec, 's': s_main, 'ss': s_spec, 't': t_nums,
        'elem': elem, 'zod': get_zodiac(dob.year), 'const': get_constellation(dob.month, dob.day),
        'r_labels': elements, 'r_vals': r_vals, 'seed': seed
    }

def render_balls_html(numbers, special=None):
    """渲染號碼球 HTML 字串"""
    html = '<div class="ball-container">'
    for n in numbers: html += f'<div class="ball">{n:02d}</div>'
    if special: html += f'<div class="ball special">{special:02d}</div>'
    return html + '</div>'

# --- 4. 介面與流程控制 ---

if not st.session_state['screenshot_mode']:
    # SPIN 按鈕 (拉桿)
    col_x, col_btn, col_y = st.columns([1, 1, 1])
    with col_btn: spin_btn = st.button("SPIN")

    col_i1, col_i2 = st.columns(2)
    with col_i1: u_name = st.text_input("玩家姓名", value=st.session_state['u_name'], placeholder="輸入姓名")
    with col_i2: u_dob = st.date_input("玩家生日", value=date(1983, 7, 15), min_value=date(1900, 1, 1), max_value=date(2030, 12, 31))

    if spin_btn:
        if not u_name: st.warning("請輸入姓名！")
        else:
            st.session_state['u_name'] = u_name
            # 未來人彩蛋
            if u_dob > date.today(): st.toast("👽 偵測到未來訊號...", icon="🛸")
            
            # 播放拉霸動畫
            ph = st.empty()
            for _ in range(6):
                fake_l = sorted(random.sample(range(1, 50), 6))
                ph.markdown(f'<div class="slot-machine-casing"><div class="machine-top"><h1 class="machine-title">SPINNING...</h1></div><div class="reel-window">{render_balls_html(fake_l)}</div></div>', unsafe_allow_html=True)
                time.sleep(0.08)
            ph.empty()
            
            # 計算真實結果
            st.session_state['last_result'] = run_quantum_simulation(u_name, u_dob, [])

# --- 5. 結果顯示區 (Slot Machine Frame) ---

if st.session_state['last_result']:
    res = st.session_state['last_result']
    
    # 構建機器本體 HTML
    machine_html = f"""
    <div class="slot-machine-casing">
        <div class="machine-top"><h1 class="machine-title">TINO LUCKY BALL</h1></div>
        <div class="status-bar">
            <div>屬性 <span class="status-highlight">{res['elem']}</span></div>
            <div>生肖 <span class="status-highlight">{res['zod']}</span></div>
            <div>星座 <span class="status-highlight">{res['const']}</span></div>
        </div>
        <div class="reel-window">
            <div class="reel-label main">大樂透 LOTTO 649</div>
            {render_balls_html(res['l'], res['ls'])}
        </div>
        <div class="reel-window">
            <div class="reel-label super">威力彩 SUPER LOTTO</div>
            {render_balls_html(res['s'], res['ss'])}
        </div>
        <div class="reel-window">
            <div class="reel-label scratch">刮刮樂尾數</div>
            <div class="scratch-num">{res['t'][0]} &nbsp; {res['t'][1]} &nbsp; {res['t'][2]}</div>
        </div>
    </div>
    """
    st.markdown(machine_html, unsafe_allow_html=True)
    
    # 能量雷達圖 (僅在非截圖模式下顯示，或依需求調整)
    with st.expander("📊 五行能量分佈分析", expanded=not st.session_state['screenshot_mode']):
        labels = res['r_labels'] + [res['r_labels'][0]]
        values = res['r_vals'] + [res['r_vals'][0]]
        fig = go.Figure(data=go.Scatterpolar(r=values, theta=labels, fill='toself', line_color='#00e5ff', fillcolor='rgba(0, 229, 255, 0.2)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=220, margin=dict(l=30, r=30, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # 功能按鈕區
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📸 產生戰報 (截圖模式)" if not st.session_state['screenshot_mode'] else "🔙 返回操作"):
            st.session_state['screenshot_mode'] = not st.session_state['screenshot_mode']
            st.rerun()
    with c2:
        if st.session_state['screenshot_mode']: st.caption("✨ 現在畫面最乾淨，請直接手機截圖")
