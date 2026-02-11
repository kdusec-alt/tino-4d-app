import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 頁面設定 ---
st.set_page_config(
    page_title="Tino Slot Machine",
    page_icon="🎰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化 Session State
if 'screenshot_mode' not in st.session_state:
    st.session_state['screenshot_mode'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# --- CSS: 加強響應式 + 標題固定在上方 ---
st.markdown("""
<style>
/* 全局 */
.stApp { 
    background-color: #000; 
    color: #f0f0f0; 
    font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
}

/* 內容區塊 */
.block-container { 
    padding-top: 1rem; 
    padding-bottom: 5rem; 
    max-width: 540px; 
}

/* 主標題 - 固定在上方 */
.main-title {
    text-align: center;
    color: #ffeb3b;
    font-size: 2.1rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-shadow: 0 0 15px #ff9900, 0 0 25px #ff5500;
    margin: 0.4rem 0 1.2rem 0;
    font-style: italic;
}

/* 輸入區 */
.input-section {
    background: rgba(20,20,20,0.7);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
    border: 1px solid #444;
}

/* 拉霸機外殼 */
.slot-machine-casing {
    background: linear-gradient(135deg, #222 0%, #0d0d0d 100%);
    border: 5px solid #ffd700;
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 0 20px rgba(255,215,0,0.25), inset 0 0 35px #000;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}

/* 機台頂部（縮小） */
.machine-top {
    text-align: center;
    background: #3a0000;
    border-radius: 10px;
    padding: 6px;
    margin-bottom: 12px;
    border: 2px solid #ff4444;
}
.machine-subtitle {
    color: #ffeb3b;
    font-weight: bold;
    font-size: 1.1rem;
    letter-spacing: 2px;
    margin: 0;
}

/* 捲軸視窗 */
.reel-window {
    background: #000;
    border: 2px solid #444;
    border-radius: 10px;
    margin-bottom: 10px;
    padding: 8px 3px;
    box-shadow: inset 0 0 15px #000;
}

/* 捲軸標籤 */
.reel-label {
    font-size: 0.75rem; 
    color: #aaa; 
    font-weight: bold; 
    text-transform: uppercase;
    margin-bottom: 5px; 
    text-align: center; 
    letter-spacing: 1.2px;
}
.reel-label.main { color: #00e5ff; text-shadow: 0 0 6px #00e5ff; }
.reel-label.super { color: #00ff88; text-shadow: 0 0 6px #00ff88; }
.reel-label.scratch { color: #ffd700; text-shadow: 0 0 6px #ffaa00; }

/* 球 */
.ball-container {
    display: flex;
    justify-content: center;
    gap: 5px;
    flex-wrap: nowrap;
    margin-top: 6px;
}
.ball {
    min-width: 36px; width: 36px; height: 36px; border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ffffff, #bbbbbb);
    color: #000; font-weight: 900; font-size: 16px;
    display: flex; align-items: center; justify-content: center;
    border: 2px solid #111;
    box-shadow: 1px 1px 4px rgba(0,0,0,0.9);
    flex-shrink: 0;
}
.ball.special {
    background: radial-gradient(circle at 30% 30%, #ff4444, #aa0000);
    color: white; border: 2px solid #ff9999;
}
.scratch-num {
    font-size: 2.1rem; font-weight: 900; color: #ffd700;
    text-shadow: 0 0 12px #ff9900; letter-spacing: 6px;
    text-align: center; margin-top: 8px;
}

/* 按鈕 */
div.stButton > button {
    width: 100px !important; height: 100px !important;
    border-radius: 50% !important;
    background: radial-gradient(circle at 30% 30%, #ff4444, #990000) !important;
    border: 5px solid #cc0000 !important;
    box-shadow: 0 10px 0 #550000, 0 18px 20px rgba(0,0,0,0.7) !important;
    color: white !important; font-weight: bold !important; font-size: 1.3rem !important;
    margin: 1rem auto !important;
}
div.stButton > button:active {
    transform: translateY(10px) !important;
    box-shadow: 0 0 0 #550000, inset 0 0 25px rgba(0,0,0,0.9) !important;
}

/* 手機適配 */
@media only screen and (max-width: 480px) {
    .main-title { font-size: 1.6rem; letter-spacing: 3px; margin: 0.6rem 0 1rem 0; }
    .ball { min-width: 30px; width: 30px; height: 30px; font-size: 13px; border-width: 1.5px; }
    .ball-container { gap: 3px; }
    .slot-machine-casing { padding: 10px; border-width: 4px; }
    .scratch-num { font-size: 1.7rem; letter-spacing: 4px; }
    div.stButton > button { width: 85px !important; height: 85px !important; font-size: 1.1rem !important; }
    .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
}

/* 隱藏多餘元素 */
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 宇宙敘事函數 ---
def generate_cosmic_story(name, element, zodiac, constellation, seed):
    random.seed(seed)
    star_events = [
        "紫微星入命，財氣微開", "破軍震盪，偏財波動", "武曲守財，金流穩固",
        "天府照命，資源匯聚", "貪狼啟動，機會流轉", "廉貞化忌，需防小人",
        "天相拱照，人緣極佳", "七殺臨宮，行動力爆發", "天梁化科，貴人暗助",
        "太陽發光，事業順遂"
    ]
    quantum_states = [
        "量子場正在重組中...", "平行宇宙分支微幅偏移", "時間軸產生細微共振",
        "未來財富態正在疊加", "機率雲開始坍縮成形", "因果線微微震盪",
        "命運熵值正在下降", "宇宙波函數即將觀測", "同步性事件頻率上升",
        "高維意識正在對齊"
    ]
    story = f"""
🌌 **宇宙敘事報告**

玩家：**{name}**  
本命元素：**{element}**  
生肖能量：**{zodiac}**  
星座頻率：**{constellation}**

✦ **星曜動態**  
{random.choice(star_events)}

✦ **量子狀態**  
{random.choice(quantum_states)}

※ 本次開啟的是『機率共振模式』  
※ 結果屬於隨機宇宙演化的一部分  
請以輕鬆心態看待此份宇宙訊息 🌠
"""
    return story

# --- 核心邏輯函數（保持原樣） ---
def get_zodiac(year):
    zodiacs = ["🐵", "🐔", "🐶", "🐷", "🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑"]
    return zodiacs[year % 12]

def get_constellation(month, day):
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    constellations = ["♑", "♒", "♓", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐"]
    if day < dates[month-1]: return constellations[month-1]
    else: return constellations[month]

def get_element_luck(year):
    last_digit = int(str(year)[-1])
    if last_digit in [0, 1]: return "金", [4, 9, 0, 5]
    if last_digit in [2, 3]: return "水", [1, 6, 4, 9]
    if last_digit in [4, 5]: return "木", [3, 8, 1, 6]
    if last_digit in [6, 7]: return "火", [2, 7, 3, 8]
    if last_digit in [8, 9]: return "土", [5, 0, 2, 7]
    return "未知", []

def calculate_dynamic_seed(name, birth_date):
    now = datetime.now()
    time_str = now.strftime("%Y%m%d%H%M%S%f")
    raw_str = f"{name}_{birth_date}_{time_str}"
    return int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)

def check_filters(numbers):
    birthday_nums = sum(1 for n in numbers if n <= 31)
    if birthday_nums > 4: return False
    sorted_nums = sorted(numbers)
    consecutive_sets = sum(1 for i in range(len(sorted_nums)-1) if sorted_nums[i+1] == sorted_nums[i] + 1)
    if consecutive_sets > 2: return False
    if all(n < 25 for n in sorted_nums): return False
    diffs = [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]
    if len(set(diffs)) == 1: return False
    return True

def generate_rational_numbers(lucky_digits, seed):
    random.seed(seed)
    for _ in range(100):
        element_pool = [n for n in range(1, 50) if n % 10 in lucky_digits]
        layer1 = random.sample(element_pool, 2)
        remaining = [n for n in range(1, 50) if n not in layer1]
        layer2 = random.sample(remaining, 4)
        final = layer1 + layer2
        if check_filters(final): return sorted(final)
    return sorted(final)

def run_simulation(name, birth_date):
    element_name, lucky_digits = get_element_luck(birth_date.year)
    zodiac = get_zodiac(birth_date.year)
    constellation = get_constellation(birth_date.month, birth_date.day)
    dynamic_seed = calculate_dynamic_seed(name, birth_date)
    
    l_main = generate_rational_numbers(lucky_digits, dynamic_seed)
    random.seed(dynamic_seed + 1)
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    random.seed(dynamic_seed + 10)
    s_main = sorted(random.sample(range(1, 39), 6))
    s_spec = random.randint(1, 8)
    
    random.seed(dynamic_seed + 2)
    base_tails = lucky_digits[:2]
    dynamic_tail = dynamic_seed % 10
    final_tails = list(set(base_tails + [dynamic_tail]))
    while len(final_tails) < 3:
        extra = random.randint(0, 9)
        if extra not in final_tails: final_tails.append(extra)
    final_tails = final_tails[:3]
    random.shuffle(final_tails)
    
    elements = ['金', '木', '水', '火', '土']
    random.seed(dynamic_seed)
    r_values = [random.randint(30, 60) for _ in range(5)]
    if element_name in elements:
        r_values[elements.index(element_name)] = random.randint(85, 95)
    
    story = generate_cosmic_story(name, element_name, zodiac, constellation, dynamic_seed)
    
    return {
        'l': l_main, 'ls': l_spec,
        's': s_main, 'ss': s_spec,
        't': final_tails,
        'elem': element_name, 'zod': zodiac, 'const': constellation,
        'r_labels': elements, 'r_values': r_values,
        'story': story
    }

def render_balls(numbers, special=None):
    html = '<div class="ball-container">'
    for n in numbers:
        html += f'<div class="ball">{n:02d}</div>'
    if special is not None:
        html += f'<div class="ball special">{special:02d}</div>'
    html += '</div>'
    return html

# ── 介面 ──
st.markdown('<div class="main-title">TINO LUCKY BALL</div>', unsafe_allow_html=True)

# 輸入區域
with st.container():
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    col1, col2 = st.columns([5,5])
    with col1:
        u_name = st.text_input("玩家姓名", "", placeholder="請輸入姓名")
    with col2:
        u_dob = st.date_input("出生日期", value=date(2000,1,1),
                              min_value=date(1900,1,1), max_value=date(2030,12,31))
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("設定")
    audit_txt = st.text_input("排除號碼", "")

# SPIN 按鈕
col_empty1, col_btn, col_empty2 = st.columns([1,2,1])
with col_btn:
    spin_btn = st.button("✨ S P I N ✨", use_container_width=True)

# 動畫與結果
if spin_btn:
    if not u_name.strip():
        st.error("請輸入姓名！")
    else:
        if u_dob > date.today():
            st.toast("🛸 來自未來的訊號...", icon="👽")
        
        placeholder = st.empty()
        
        for _ in range(6):
            fake_l = sorted(random.sample(range(1,50),6))
            fake_ls = random.randint(1,49)
            fake_s = sorted(random.sample(range(1,39),6))
            fake_ss = random.randint(1,8)
            fake_t = random.sample(range(0,10),3)
            placeholder.markdown(f"""
<div class="slot-machine-casing">
<div class="machine-top"><div class="machine-subtitle">SPINNING...</div></div>
<div class="reel-window"><div class="reel-label main">大樂透</div>{render_balls(fake_l, fake_ls)}</div>
<div class="reel-window"><div class="reel-label super">威力彩</div>{render_balls(fake_s, fake_ss)}</div>
<div class="reel-window"><div class="reel-label scratch">刮刮樂</div><div class="scratch-num">{fake_t[0]} {fake_t[1]} {fake_t[2]}</div></div>
</div>
""", unsafe_allow_html=True)
            time.sleep(0.09)
        
        placeholder.empty()
        
        result = run_simulation(u_name.strip(), u_dob)
        st.session_state['last_result'] = result

# ── 結果顯示 ──
if st.session_state.get('last_result'):
    res = st.session_state['last_result']
    
    # 能量分析（雷達圖）放在最上面
    with st.expander("📊 能量分析", expanded=True):
        r_vals = res['r_values'] + [res['r_values'][0]]
        r_labs = res['r_labels'] + [res['r_labels'][0]]
        fig = go.Figure(data=go.Scatterpolar(
            r=r_vals, theta=r_labs, fill='toself',
            line_color='#00e5ff', fillcolor='rgba(0,229,255,0.18)',
            marker=dict(color='#ffffff', size=5)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0,100]),
                angularaxis=dict(tickfont=dict(size=11, color='#ddd'), rotation=90, direction='clockwise'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            height=260,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 拉霸機結果
    t = res['t']
    st.markdown(f"""
<div class="slot-machine-casing">
<div class="machine-top"><div class="machine-subtitle">YOUR LUCKY DRAW</div></div>
<div class="reel-window"><div class="reel-label main">大樂透 LOTTO</div>{render_balls(res['l'], res['ls'])}</div>
<div class="reel-window"><div class="reel-label super">威力彩 SUPER</div>{render_balls(res['s'], res['ss'])}</div>
<div class="reel-window"><div class="reel-label scratch">刮刮樂 SCRATCH</div><div class="scratch-num">{t[0]} &nbsp; {t[1]} &nbsp; {t[2]}</div></div>
</div>
""", unsafe_allow_html=True)
    
    # 狀態條
    st.markdown(f"""
<div style="display:flex; justify-content:space-between; background:#111; border-radius:10px; padding:10px; margin:1rem 0; border:1px solid #333;">
    <div>屬性 <span style="color:#00e5ff; font-weight:bold;">{res['elem']}</span></div>
    <div>生肖 <span style="color:#00e5ff; font-weight:bold;">{res['zod']}</span></div>
    <div>星座 <span style="color:#00e5ff; font-weight:bold;">{res['const']}</span></div>
</div>
""", unsafe_allow_html=True)
    
    # 宇宙敘事（最下方）
    with st.expander("🌌 宇宙敘事報告", expanded=False):
        st.markdown(res['story'])
        st.caption("TINO Cosmic Destiny Engine • 娛樂用途 • 隨機生成")
    
    # 戰報模式按鈕
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state['screenshot_mode']:
            if st.button("📸 戰報模式"):
                st.session_state['screenshot_mode'] = True
                st.rerun()
        else:
            if st.button("🔙 返回正常模式"):
                st.session_state['screenshot_mode'] = False
                st.rerun()
