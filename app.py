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

# --- CSS ---
st.markdown("""
<style>
.stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
.block-container { padding-top: 1rem; padding-bottom: 5rem; max-width: 580px; }

.main-title {
    text-align: center;
    color: #ffeb3b;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 5px;
    text-shadow: 0 0 15px #ff9900;
    margin: 0.5rem 0 1.5rem 0;
}

命理區塊 {
    background: rgba(15,15,35,0.7);
    border: 1px solid #4444ff;
    border-radius: 12px;
    padding: 1.2rem;
    margin: 1.5rem 0;
}

.reel-window, .slot-machine-casing { /* 原有樣式保持 */ }
/* ... 其他原有 CSS 保持不變 ... */
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
    return f"""
**宇宙敘事報告**

玩家：{name}  
本命元素：{element}  
生肖能量：{zodiac}  
星座頻率：{constellation}

**星曜動態**  
{random.choice(star_events)}

**量子狀態**  
{random.choice(quantum_states)}

※ 本次開啟的是『機率共振模式』  
※ 結果屬於隨機宇宙演化的一部分  
請以輕鬆心態看待此份宇宙訊息 🌠
"""

# --- 核心邏輯 ---
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

def calculate_daily_fate_seed(name, birth_date):
    """每天相同的命理種子：只用日期 + 姓名 + 生日，不含時分秒"""
    today = datetime.now().date()
    raw_str = f"{name}_{birth_date}_{today.year}{today.month:02d}{today.day:02d}"
    return int(hashlib.sha256(raw_str.encode()).hexdigest(), 16)

def calculate_dynamic_seed(name, birth_date):
    """號碼用的動態種子，包含時間，每次不同"""
    now = datetime.now()
    time_str = now.strftime("%Y%m%d%H%M%S%f")
    raw_str = f"{name}_{birth_date}_{time_str}"
    return int(hashlib.sha256(raw_str.encode()).hexdigest(), 16)

def run_simulation(name, birth_date):
    element_name, lucky_digits = get_element_luck(birth_date.year)
    zodiac = get_zodiac(birth_date.year)
    constellation = get_constellation(birth_date.month, birth_date.day)
    
    # 每天固定的命理種子
    fate_seed = calculate_daily_fate_seed(name, birth_date)
    
    # 五行能量值使用每天固定種子
    elements = ['金', '木', '水', '火', '土']
    random.seed(fate_seed)
    r_values = [random.randint(30, 60) for _ in range(5)]
    if element_name in elements:
        idx = elements.index(element_name)
        r_values[idx] = random.randint(85, 95)
    
    # 宇宙敘事也使用每天固定種子
    story = generate_cosmic_story(name, element_name, zodiac, constellation, fate_seed)
    
    # 號碼部分使用動態種子（每次不同）
    dynamic_seed = calculate_dynamic_seed(name, birth_date)
    
    l_main = generate_rational_numbers(lucky_digits, dynamic_seed)  # 假設你有這個函數
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
    
    return {
        'l': l_main, 'ls': l_spec,
        's': s_main, 'ss': s_spec,
        't': final_tails,
        'elem': element_name, 'zod': zodiac, 'const': constellation,
        'r_labels': elements, 'r_values': r_values,
        'story': story
    }

# 假設你原本有這些函數，請保留或補上
def generate_rational_numbers(lucky_digits, seed):
    # 你原本的實作
    random.seed(seed)
    # ... 你的邏輯 ...
    return sorted(random.sample(range(1,50), 6))  # 暫時用簡單版替代

def render_balls(numbers, special=None):
    html = '<div style="display:flex; justify-content:center; gap:6px; margin:8px 0;">'
    for n in numbers:
        html += f'<div style="width:38px;height:38px;border-radius:50%;background:#ddd;color:#000;font-weight:bold;display:flex;align-items:center;justify-content:center;border:2px solid #333;">{n:02d}</div>'
    if special is not None:
        html += f'<div style="width:38px;height:38px;border-radius:50%;background:#c00;color:white;font-weight:bold;display:flex;align-items:center;justify-content:center;border:2px solid #900;">{special:02d}</div>'
    html += '</div>'
    return html

# --- 介面 ---
st.title("TINO LUCKY BALL")

col1, col2 = st.columns(2)
with col1:
    u_name = st.text_input("玩家姓名", "")
with col2:
    u_dob = st.date_input("出生日期", value=date(2000,1,1))

if st.button("SPIN"):
    if not u_name:
        st.warning("請輸入姓名")
    else:
        with st.spinner("宇宙運算中..."):
            time.sleep(1.5)  # 模擬動畫時間
            result = run_simulation(u_name, u_dob)
            st.session_state['last_result'] = result

# 顯示結果
if 'last_result' in st.session_state:
    res = st.session_state['last_result']
    
    # 命理綜合區塊
    st.markdown("### 🌌 命理能量綜合分析")
    
    col_chart, col_story = st.columns([5, 4])
    
    with col_chart:
        r_vals = res['r_values'] + [res['r_values'][0]]
        r_labs = res['r_labels'] + [res['r_labels'][0]]
        fig = go.Figure(data=go.Scatterpolar(
            r=r_vals, theta=r_labs, fill='toself',
            line_color='#00ccff', fillcolor='rgba(0,200,255,0.25)',
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0,100])),
            showlegend=False, height=300, margin=dict(l=20,r=20,t=20,b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_story:
        st.markdown(res['story'])
    
    # 開獎結果區塊
    st.markdown("### 🎰 今日幸運號碼")
    t = res['t']
    st.markdown(f"""
    大樂透：{render_balls(res['l'], res['ls'])}
    威力彩：{render_balls(res['s'], res['ss'])}
    刮刮樂尾數：**{t[0]}  {t[1]}  {t[2]}**
    """, unsafe_allow_html=True)
