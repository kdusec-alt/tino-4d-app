import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 1. 頁面與 iPhone 適配設定 ---
st.set_page_config(
    page_title="Tino Slot Machine", 
    page_icon="🎰", 
    layout="centered", # 改回 centered 讓手機版更像一台直立機器
    initial_sidebar_state="collapsed"
)

# 初始化 Session State
if 'screenshot_mode' not in st.session_state:
    st.session_state['screenshot_mode'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# --- CSS: 打造整台吃角子老虎機的外框 ---
st.markdown("""
    <style>
    /* 全局設定 */
    .stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; max-width: 600px; } /* 限制寬度像手機 */

    /* === 拉霸機外殼 (The Machine Casing) === */
    .slot-machine-casing {
        background: linear-gradient(135deg, #222 0%, #111 100%);
        border: 4px solid #ffd700;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3), inset 0 0 50px #000;
        margin-bottom: 20px;
        position: relative;
    }
    
    /* 頂部裝飾燈 */
    .machine-top {
        text-align: center;
        background: #330000;
        border-radius: 10px;
        padding: 5px;
        margin-bottom: 15px;
        border: 2px solid #ff3333;
        box-shadow: 0 0 10px #ff0000;
    }
    .machine-title {
        color: #ffeb3b; font-weight: 900; font-size: 1.5em; letter-spacing: 2px;
        text-shadow: 0 0 5px #ff0000; margin: 0;
    }

    /* === 三排捲軸視窗 (The Reels) === */
    .reel-window {
        background: #000;
        border: 3px solid #555;
        border-radius: 10px;
        margin-bottom: 10px;
        padding: 10px 5px;
        box-shadow: inset 0 0 15px #000;
        position: relative;
        overflow: hidden;
    }
    
    /* 捲軸標籤 */
    .reel-label {
        position: absolute; top: 2px; left: 5px;
        font-size: 0.7em; color: #00e5ff; font-weight: bold; text-transform: uppercase;
        background: rgba(0,0,0,0.8); padding: 2px 5px; border-radius: 4px;
        z-index: 2;
    }
    .reel-label.super { color: #00ff00; }
    .reel-label.scratch { color: #ffd700; }

    /* 數字球樣式 (iPhone 優化) */
    .ball-container {
        display: flex; justify-content: center; gap: 4px; flex-wrap: nowrap; margin-top: 15px; overflow-x: auto;
    }
    .ball {
        min-width: 38px; width: 38px; height: 38px; border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #fff, #ddd);
        color: #000; font-weight: 900; font-size: 18px;
        display: flex; align-items: center; justify-content: center;
        border: 2px solid #222;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .ball.special {
        background: radial-gradient(circle at 30% 30%, #ff4444, #aa0000);
        color: white; border: 2px solid #ffaaaa;
    }
    .scratch-num {
        font-size: 2em; font-weight: 900; color: #ffd700; 
        text-shadow: 0 0 10px #ff0000; letter-spacing: 5px;
        text-align: center; margin-top: 10px;
    }

    /* === 拉桿按鈕 === */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 60px; 
        background: linear-gradient(to bottom, #ff4444, #990000); 
        color: white; font-size: 1.4em; font-weight: 800; border: 4px solid #ffd700; 
        box-shadow: 0 5px 0 #550000, 0 10px 20px rgba(0,0,0,0.6);
        text-transform: uppercase;
    }
    .stButton>button:active {
        transform: translateY(5px);
        box-shadow: 0 0 0 #550000;
    }

    /* 儀表板 */
    .status-bar {
        display: flex; justify-content: space-around;
        background: #222; border-radius: 8px; padding: 5px; margin-bottom: 10px;
        border: 1px solid #444;
    }
    .status-txt { color: #00e5ff; font-weight: bold; font-size: 0.9em; }
    
    /* 隱藏預設 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心邏輯 (V10.1) ---

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

# --- 第三層：反人性過濾 ---
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
        # 第一層：五行 (2顆)
        layer1_nums = random.sample(element_pool, 2)
        remaining_pool = [n for n in range(1, 50) if n not in layer1_nums]
        # 第二層：隨機 (4顆)
        layer2_nums = random.sample(remaining_pool, 4)
        final_set = layer1_nums + layer2_nums
        # 第三層：過濾
        if check_filters(final_set):
            return sorted(final_set)
    return sorted(final_set)

def run_simulation(name, birth_date, audit_list):
    element_name, lucky_digits = get_element_luck(birth_date.year)
    zodiac = get_zodiac(birth_date.year)
    constellation = get_constellation(birth_date.month, birth_date.day)
    dynamic_seed = calculate_dynamic_seed(name, birth_date)
    
    # 大樂透
    l_main = generate_rational_numbers(lucky_digits, dynamic_seed)
    random.seed(dynamic_seed + 1)
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    # 威力彩 (簡化邏輯，快速生成)
    random.seed(dynamic_seed + 10)
    s_main = sorted(random.sample(range(1, 39), 6))
    s_spec = random.randint(1, 8)
    
    # 刮刮樂 (確保五行邏輯存在)
    # 邏輯：必定包含五行幸運數，加上當下流秒數
    random.seed(dynamic_seed + 2)
    base_tails = lucky_digits[:2] # 取前兩個最幸運的
    dynamic_tail = (dynamic_seed % 10)
    final_tails = list(set(base_tails + [dynamic_tail]))
    while len(final_tails) < 3:
        extra = random.randint(0, 9)
        if extra not in final_tails: final_tails.append(extra)
    final_tails = final_tails[:3]
    random.shuffle(final_tails)
    
    # 雷達圖
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

# 側邊欄
with st.sidebar:
    st.header("⚙️")
    audit_txt = st.text_input("排除號碼", "")
    st.caption("設定後請按拉霸")

# --- 輸入區 (截圖模式隱藏) ---
if not st.session_state['screenshot_mode']:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        u_name = st.text_input("玩家姓名", value="", placeholder="輸入姓名")
    with col_input2:
        # 修正：日期範圍擴大到 2030
        u_dob = st.date_input("玩家生日", value=date(2000, 1, 1), 
                              min_value=date(1900, 1, 1), 
                              max_value=date(2030, 12, 31)) # 開放到 2030

    st.write("") 

    if st.button("🔴 拉動拉霸 (SPIN)"):
        if not u_name:
            st.warning("⚠️ 請輸入姓名！")
        else:
            # --- 未來人彩蛋邏輯 ---
            if u_dob > date.today():
                st.toast("🛸 嗶嗶！偵測到未來人訊號！", icon="👽")
                st.info(f"來自 {u_dob.year} 年的朋友 {u_name}，這期號碼你應該早就知道了吧？😏")
                time.sleep(1.5) # 讓使用者看清楚吐槽
            
            st.session_state['u_name'] = u_name
            
            # 準備容器
            placeholder = st.empty()
            
            # 動畫：模擬拉霸機三排轉動
            for i in range(6): 
                fake_l = sorted(random.sample(range(1, 50), 6))
                fake_ls = random.randint(1, 49)
                fake_scratch = random.sample(range(0, 10), 3)
                
                # 渲染動畫幀 (假資料)
                placeholder.markdown(f"""
                <div class="slot-machine-casing">
                    <div class="machine-top"><h1 class="machine-title">🎰 JACKPOT SPINNING...</h1></div>
                    
                    <div class="reel-window" style="opacity:0.7">
                        <div class="reel-label">ROW 1</div>
                        {render_balls(fake_l, fake_ls)}
                    </div>
                    
                    <div class="reel-window" style="opacity:0.7">
                        <div class="reel-label super">ROW 2</div>
                        {render_balls(fake_l, fake_ls)}
                    </div>
                    
                    <div class="reel-window" style="opacity:0.7">
                        <div class="reel-label scratch">ROW 3</div>
                        <div class="scratch-num">{fake_scratch[0]} {fake_scratch[1]} {fake_scratch[2]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.1)
            
            placeholder.empty()
            
            # 計算真實結果
            result = run_simulation(u_name, u_dob, audit_list if 'audit_list' in locals() else [])
            st.session_state['last_result'] = result

# --- 結果顯示區 (機器本體) ---
if st.session_state['last_result']:
    res = st.session_state['last_result']
    t = res['t']
    
    # 整個拉霸機的 HTML 結構
    st.markdown(f"""
    <div class="slot-machine-casing">
        <div class="machine-top">
            <h1 class="machine-title">🎰 TINO LUCKY BALL</h1>
        </div>
        
        <div class="status-bar">
            <span class="status-txt">{res['elem']}</span>
            <span class="status-txt">{res['zod']}</span>
            <span class="status-txt">{res['const']}</span>
        </div>

        <div class="reel-window">
            <div class="reel-label">大樂透 LOTTO</div>
            {render_balls(res['l'], res['ls'])}
        </div>

        <div class="reel-window" style="border-color: #00ff00;">
            <div class="reel-label super">威力彩 SUPER</div>
            {render_balls(res['s'], res['ss'])}
        </div>

        <div class="reel-window" style="border-color: #ffd700;">
            <div class="reel-label scratch">刮刮樂 SCRATCH</div>
            <div class="scratch-num">
                {t[0]} &nbsp; {t[1]} &nbsp; {t[2]}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 雷達圖 (放機器下面)
    with st.expander("📊 查看五行能量分佈 (Analysis)", expanded=True):
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

    # 截圖按鈕區
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if not st.session_state['screenshot_mode']:
            if st.button("📸 開啟戰報模式"):
                st.session_state['screenshot_mode'] = True
                st.rerun()
        else:
            if st.button("🔙 返回輸入"):
                st.session_state['screenshot_mode'] = False
                st.rerun()
