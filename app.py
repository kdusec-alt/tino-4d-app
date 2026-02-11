import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 1. 系統初始化與頁面配置 ---
st.set_page_config(
    page_title="Tino Lucky Ball", 
    page_icon="🌌", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化 Session State
if 'screenshot_mode' not in st.session_state:
    st.session_state['screenshot_mode'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None
if 'u_name' not in st.session_state:
    st.session_state['u_name'] = ""

# --- 2. 完整 CSS 渲染引擎 (包含 iPhone 響應式佈局) ---
st.markdown("""
<style>
    .stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; max-width: 500px !important; }

    /* 拉霸機外殼 */
    .slot-machine-casing {
        background: linear-gradient(135deg, #222 0%, #0d0d0d 100%);
        border: 4px solid #ffd700;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.3), inset 0 0 50px #000;
        margin-bottom: 20px;
        position: relative;
    }
    
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

    .reel-window {
        background: #000; border: 2px solid #333; border-radius: 10px;
        margin-bottom: 12px; padding: 10px 2px; box-shadow: inset 0 0 15px #000;
        position: relative;
    }
    .reel-label {
        font-size: 0.7em; color: #888; font-weight: bold; text-transform: uppercase;
        margin-bottom: 5px; text-align: center; letter-spacing: 1.5px;
    }
    .reel-label.main { color: #00e5ff; }
    .reel-label.super { color: #00ff00; }
    .reel-label.scratch { color: #ffd700; }

    .ball-container { display: flex; justify-content: center; gap: 4px; flex-wrap: nowrap; width: 100%; }
    .ball {
        width: 8.5vw; height: 8.5vw; max-width: 36px; max-height: 36px; border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ffffff, #bbbbbb);
        color: #000; font-weight: 900; font-size: 3.8vw; max-font-size: 16px;
        display: flex; align-items: center; justify-content: center;
        border: 1.5px solid #000; box-shadow: 1px 1px 4px rgba(0,0,0,0.8); flex-shrink: 0;
    }
    .ball.special { background: radial-gradient(circle at 30% 30%, #ff3333, #990000); color: white; border: 1.5px solid #ff9999; }
    .scratch-num { font-size: 2em; font-weight: 900; color: #ffd700; text-shadow: 0 0 12px #ff9900; letter-spacing: 12px; text-align: center; }

    /* 拉桿按鈕 */
    .stButton { text-align: center; }
    div.stButton > button {
        width: 90px !important; height: 90px !important; border-radius: 50% !important;
        background: radial-gradient(circle at 30% 30%, #ff4444, #990000) !important;
        border: 4px solid #cc0000 !important;
        box-shadow: 0 8px 0 #550000, 0 15px 20px rgba(0,0,0,0.6) !important;
        color: white !important; font-weight: bold !important; font-size: 1.1em !important; margin: 15px auto !important;
    }
    div.stButton > button:active { transform: translateY(8px) !important; box-shadow: 0 0 0 #550000, inset 0 0 20px rgba(0,0,0,0.8) !important; }

    .status-bar { display: flex; justify-content: space-between; background: #111; border-radius: 8px; padding: 8px 15px; margin-bottom: 12px; border: 1px solid #333; }
    .status-txt { color: #fff; font-size: 0.8em; }
    .status-highlight { color: #00e5ff; font-weight: bold; margin-left: 3px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心邏輯層 (整合宇宙敘事) ---

def get_zodiac(year):
    zods = ["🐵", "🐔", "🐶", "🐷", "🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑"]
    return zods[year % 12]

def get_constellation(month, day):
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    consts = ["♑", "♒", "♓", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐"]
    return consts[month-1] if day < dates[month-1] else consts[month]

def get_element_luck(year):
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
    if sum(1 for n in numbers if n <= 31) > 4: return False
    sn = sorted(numbers)
    if sum(1 for i in range(len(sn)-1) if sn[i+1] == sn[i]+1) > 2: return False
    if all(n < 25 for n in sn): return False
    return True

def generate_cosmic_story(name, element, zodiac, constellation, seed):
    """豪華宇宙敘事生成器"""
    random.seed(seed)
    star_events = ["紫微星入命，財氣微開", "破軍震盪，偏財波動", "武曲守財，金流穩固", "天府照命，資源匯聚", "貪狼啟動，機會流轉"]
    quantum_states = ["量子場正在重組", "平行宇宙分支微幅偏移", "時間軸產生細微共振", "未來財富態正在疊加", "機率雲開始坍縮"]
    
    return f"""
    🌌 宇宙敘事報告

    玩家：{name}
    本命元素：{element}
    生肖能量：{zodiac}
    星座頻率：{constellation}

    ✦ 星曜狀態：
    {random.choice(star_events)}

    ✦ 量子動態：
    {random.choice(quantum_states)}

    ※ 本次開啟的是『機率共振模式』
    ※ 結果屬於隨機宇宙演化的一部分
    """

def run_simulation(name, dob, audit_list):
    elem, lucky = get_element_luck(dob.year)
    zodiac = get_zodiac(dob.year)
    const = get_constellation(dob.month, dob.day)
    seed = int(hashlib.sha256(f"{name}{dob}{datetime.now().strftime('%f')}".encode()).hexdigest(), 16)
    
    # 核心選號邏輯
    random.seed(seed)
    # 大樂透 (Layer 1 + Layer 2)
    l_pool = [n for n in range(1, 50) if n % 10 in lucky]
    l1 = random.sample(l_pool, 2)
    l2 = random.sample([n for n in range(1, 50) if n not in l1], 4)
    l_main = sorted(l1 + l2)
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    # 生成敘事報告
    story = generate_cosmic_story(name, elem, zodiac, const, seed)
    
    elements = ['金', '木', '水', '火', '土']
    r_vals = [random.randint(40, 70) for _ in range(5)]
    if elem in elements: r_vals[elements.index(elem)] = 95

    return {
        'l': l_main, 'ls': l_spec, 't': random.sample(range(10), 3),
        'elem': elem, 'zod': zodiac, 'const': const, 'story': story,
        'r_labels': elements, 'r_vals': r_vals
    }

def render_balls(numbers, special=None):
    html = '<div class="ball-container">'
    for n in numbers: html += f'<div class="ball">{n:02d}</div>'
    if special: html += f'<div class="ball special">{special:02d}</div>'
    return html + '</div>'

# --- 4. 介面流程 ---

st.markdown("<h1>🎱 Tino Lucky Ball</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#666; font-size:0.8em; margin-bottom:20px;'>V10.6 COSMIC DESTINY ENGINE</div>", unsafe_allow_html=True)

if not st.session_state['screenshot_mode']:
    col_x, col_btn, col_y = st.columns([1, 1, 1])
    with col_btn: spin_btn = st.button("SPIN")
    
    c1, c2 = st.columns(2)
    with c1: u_name = st.text_input("玩家姓名", value="鄭廷暘")
    with c2: u_dob = st.date_input("生日", value=date(1983, 7, 15))

    if spin_btn:
        ph = st.empty()
        for _ in range(5):
            ph.markdown('<div class="slot-machine-casing" style="opacity:0.6;"><h1 style="text-align:center; color:#ffd700;">SCANNING...</h1></div>', unsafe_allow_html=True)
            time.sleep(0.1)
        ph.empty()
        st.session_state['last_result'] = run_simulation(u_name, u_dob, [])

if st.session_state['last_result']:
    res = st.session_state['last_result']
    
    # 顯示拉霸機結果
    st.markdown(f"""
    <div class="slot-machine-casing">
        <div class="status-bar">
            <div>屬性 <span class="status-highlight">{res['elem']}</span></div>
            <div>生肖 <span class="status-highlight">{res['zod']}</span></div>
            <div>星座 <span class="status-highlight">{res['const']}</span></div>
        </div>
        <div class="reel-window">
            <div class="reel-label main">大樂透 LOTTO 649</div>
            {render_balls(res['l'], res['ls'])}
        </div>
        <div class="reel-window">
            <div class="reel-label scratch">刮刮樂尾數</div>
            <div class="scratch-num">{res['t'][0]} &nbsp; {res['t'][1]} &nbsp; {res['t'][2]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 🌠 新增宇宙敘事層
    with st.expander("🌌 宇宙敘事層 (Cosmic Report)", expanded=False):
        st.markdown(res['story'])

    # 雷達圖分析
    with st.expander("📊 五行能量分析"):
        fig = go.Figure(data=go.Scatterpolar(r=res['r_vals']+[res['r_vals'][0]], theta=res['r_labels']+[res['r_labels'][0]], fill='toself', fillcolor='rgba(0, 229, 255, 0.2)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=220, margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    if st.button("📸 切換模式"): st.session_state['screenshot_mode'] = not st.session_state['screenshot_mode']; st.rerun()
