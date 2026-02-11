import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 1. 頁面設定 ---
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

# --- CSS: 賭城黑金風格 ---
st.markdown("""
<style>
/* 全局設定 */
.stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
.block-container { padding-top: 1rem; padding-bottom: 5rem; max-width: 500px; }

/* 拉霸機外殼 */
.slot-machine-casing {
    background: linear-gradient(135deg, #222 0%, #0d0d0d 100%);
    border: 6px solid #ffd700;
    border-radius: 25px;
    padding: 20px;
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.2), inset 0 0 60px #000;
    margin-bottom: 20px;
    position: relative;
}

/* 頂部裝飾燈 */
.machine-top {
    text-align: center;
    background: #4a0000;
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 20px;
    border: 3px solid #ff3333;
    box-shadow: 0 0 15px #ff0000, inset 0 0 20px #000;
}
.machine-title {
    color: #ffeb3b; font-weight: 900; font-size: 1.8em; letter-spacing: 3px;
    text-shadow: 0 0 10px #ff0000; margin: 0; font-style: italic;
}

/* 捲軸視窗 */
.reel-window {
    background: #000;
    border: 2px solid #444;
    border-radius: 10px;
    margin-bottom: 12px;
    padding: 10px 5px;
    box-shadow: inset 0 0 20px #000;
    position: relative;
    overflow: hidden;
}

/* 捲軸標籤 */
.reel-label {
    font-size: 0.7em; color: #888; font-weight: bold; text-transform: uppercase;
    margin-bottom: 5px; text-align: center; letter-spacing: 2px;
}
.reel-label.main { color: #00e5ff; text-shadow: 0 0 5px #00e5ff; }
.reel-label.super { color: #00ff00; text-shadow: 0 0 5px #00ff00; }
.reel-label.scratch { color: #ffd700; text-shadow: 0 0 5px #ffd700; }

/* 數字球樣式 */
.ball-container {
    display: flex; justify-content: center; gap: 5px; flex-wrap: nowrap; margin-top: 5px; overflow-x: auto;
}
.ball {
    min-width: 36px; width: 36px; height: 36px; border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ffffff, #bbbbbb);
    color: #000; font-weight: 900; font-size: 16px;
    display: flex; align-items: center; justify-content: center;
    border: 2px solid #000;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.8);
    font-family: 'Arial', sans-serif;
}
.ball.special {
    background: radial-gradient(circle at 30% 30%, #ff3333, #990000);
    color: white; border: 2px solid #ff9999;
}
.scratch-num {
    font-size: 2em; font-weight: 900; color: #ffd700; 
    text-shadow: 0 0 15px #ff9900; letter-spacing: 8px;
    text-align: center; margin-top: 5px;
}

/* 擬真拉桿按鈕 */
div.stButton > button {
    width: 100px !important;
    height: 100px !important;
    border-radius: 50% !important;
    background: radial-gradient(circle at 30% 30%, #ff4444, #990000) !important;
    border: 4px solid #cc0000 !important;
    box-shadow: 0 10px 0 #550000, 0 20px 20px rgba(0,0,0,0.6), inset 0 0 20px rgba(0,0,0,0.5) !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 1.2em !important;
    margin: 0 auto !important;
    display: block !important;
    position: relative !important;
    z-index: 10 !important;
}
div.stButton > button:active {
    transform: translateY(10px) !important;
    box-shadow: 0 0 0 #550000, inset 0 0 20px rgba(0,0,0,0.8) !important;
}

/* 儀表板 */
.status-bar {
    display: flex; justify-content: space-between;
    background: #111; border-radius: 8px; padding: 8px 15px; margin-bottom: 15px;
    border: 1px solid #333;
}
.status-txt { color: #fff; font-size: 0.9em; }
.status-highlight { color: #00e5ff; font-weight: bold; margin-left: 5px;}

#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. 核心邏輯 ---
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
    seed_val = int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)
    return seed_val

def check_filters(numbers):
    birthday_nums = sum(1 for n in numbers if n <= 31)
    if birthday_nums > 4: return False
    sorted_nums = sorted(numbers)
    consecutive_sets = 0
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i+1] == sorted_nums[i] + 1:
            consecutive_sets += 1
    if consecutive_sets > 2: return False
    if all(n < 25 for n in sorted_nums): return False
    diffs = [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]
    if len(set(diffs)) == 1: return False
    return True

def generate_rational_numbers(lucky_digits, seed):
    random.seed(seed)
    for _ in range(100):
        element_pool = [n for n in range(1, 50) if n % 10 in lucky_digits]
        layer1_nums = random.sample(element_pool, 2)
        remaining_pool = [n for n in range(1, 50) if n not in layer1_nums]
        layer2_nums = random.sample(remaining_pool, 4)
        final_set = layer1_nums + layer2_nums
        if check_filters(final_set): return sorted(final_set)
    return sorted(final_set)

def run_simulation(name, birth_date, audit_list):
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
    dynamic_tail = (dynamic_seed % 10)
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
        idx = elements.index(element_name)
        r_values[idx] = random.randint(85, 95)
        
    return {
        'l': l_main, 'ls': l_spec, 's': s_main, 'ss': s_spec, 't': final_tails,
        'elem': element_name, 'zod': zodiac, 'const': constellation,
        'r_labels': elements, 'r_values': r_values
    }

def render_balls(numbers, special=None):
    html = '<div class="ball-container">'
    for n in numbers:
        html += f'<div class="ball">{n:02d}</div>'
    if special is not None:
        html += f'<div class="ball special">{special:02d}</div>'
    html += '</div>'
    return html

# --- 3. App 介面 ---
with st.sidebar:
    st.header("⚙️")
    audit_txt = st.text_input("排除號碼", "")

if not st.session_state['screenshot_mode']:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        u_name = st.text_input("玩家姓名", value="", placeholder="輸入姓名")
    with col_input2:
        u_dob = st.date_input("玩家生日", value=date(2000, 1, 1), 
                              min_value=date(1900, 1, 1), max_value=date(2030, 12, 31))

    st.write("") 
    
    col_x, col_btn, col_y = st.columns([1, 1, 1])
    with col_btn:
        spin_btn = st.button("SPIN") # 拉桿按鈕

    if spin_btn:
        if not u_name:
            st.warning("⚠️ 請輸入姓名！")
        else:
            if u_dob > date.today():
                st.toast("🛸 來自未來的訊號...", icon="👽")
            
            st.session_state['u_name'] = u_name
            placeholder = st.empty()
            
            # 動畫播放 (修正縮排)
            for i in range(5): 
                fake_l = sorted(random.sample(range(1, 50), 6))
                fake_ls = random.randint(1, 49)
                fake_s = sorted(random.sample(range(1, 39), 6))
                fake_ss = random.randint(1, 8)
                fake_scratch = random.sample(range(0, 10), 3)
                
                # 這裡最重要：所有 HTML 靠左對齊，不要有縮排！
                placeholder.markdown(f"""
<div class="slot-machine-casing">
<div class="machine-top"><h1 class="machine-title">SPINNING...</h1></div>
<div class="reel-window"><div class="reel-label main">大樂透</div>{render_balls(fake_l, fake_ls)}</div>
<div class="reel-window"><div class="reel-label super">威力彩</div>{render_balls(fake_s, fake_ss)}</div>
<div class="reel-window"><div class="reel-label scratch">刮刮樂</div><div class="scratch-num">{fake_scratch[0]} {fake_scratch[1]} {fake_scratch[2]}</div></div>
</div>""", unsafe_allow_html=True)
                time.sleep(0.08)
            
            placeholder.empty()
            result = run_simulation(u_name, u_dob, audit_list if 'audit_list' in locals() else [])
            st.session_state['last_result'] = result

# --- 結果顯示區 (修正縮排) ---
if st.session_state['last_result']:
    res = st.session_state['last_result']
    t = res['t']
    
    # 這裡也一樣：HTML 靠左對齊
    st.markdown(f"""
<div class="slot-machine-casing">
<div class="machine-top"><h1 class="machine-title">TINO LUCKY BALL</h1></div>
<div class="status-bar">
<div>屬性 <span class="status-highlight">{res['elem']}</span></div>
<div>生肖 <span class="status-highlight">{res['zod']}</span></div>
<div>星座 <span class="status-highlight">{res['const']}</span></div>
</div>
<div class="reel-window"><div class="reel-label main">大樂透 LOTTO</div>{render_balls(res['l'], res['ls'])}</div>
<div class="reel-window"><div class="reel-label super">威力彩 SUPER</div>{render_balls(res['s'], res['ss'])}</div>
<div class="reel-window"><div class="reel-label scratch">刮刮樂 SCRATCH</div><div class="scratch-num">{t[0]} &nbsp; {t[1]} &nbsp; {t[2]}</div></div>
</div>""", unsafe_allow_html=True)
    
    with st.expander("📊 能量分析", expanded=False):
        r_vals = res['r_values'] + [res['r_values'][0]]
        r_labs = res['r_labels'] + [res['r_labels'][0]]
        fig = go.Figure(data=go.Scatterpolar(
            r=r_vals, theta=r_labs, fill='toself',
            line_color='#00e5ff', fillcolor='rgba(0, 229, 255, 0.2)',
            marker=dict(color='#fff', size=4)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100]),
                angularaxis=dict(tickfont=dict(size=10, color='#aaa'), rotation=90, direction='clockwise'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, height=200, margin=dict(l=30, r=30, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if not st.session_state['screenshot_mode']:
            if st.button("📸 戰報模式"):
                st.session_state['screenshot_mode'] = True
                st.rerun()
        else:
            if st.button("🔙 返回"):
                st.session_state['screenshot_mode'] = False
                st.rerun()
