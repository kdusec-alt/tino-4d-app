import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# ==========================================
# 1. 系統核心配置 (System Config)
# ==========================================
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

# ==========================================
# 2. CSS 渲染引擎 (Pro Grade UI)
# ==========================================
st.markdown("""
<style>
    /* 全局設定：黑金宇宙風格 */
    .stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    
    /* 容器優化：手機版強制邊距 */
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 5rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important;
        max-width: 500px !important; 
    }

    /* --- 區域 A: 命理戰報 (定數區) --- */
    .fate-container {
        background: linear-gradient(180deg, #1a0505 0%, #000 100%);
        border: 2px solid #ff4444; border-radius: 15px; padding: 12px;
        margin-bottom: 15px; box-shadow: 0 0 15px rgba(255, 68, 68, 0.2);
    }
    .fate-header { 
        color: #ffd700; font-size: 1.1em; font-weight: bold; 
        border-bottom: 1px solid #444; padding-bottom: 5px; margin-bottom: 10px; 
    }
    .fate-text { font-size: 0.9em; line-height: 1.6; color: #ddd; }
    .highlight { color: #00e5ff; font-weight: bold; }
    .timestamp { font-size: 0.7em; color: #666; text-align: right; margin-top: 8px; border-top: 1px solid #333; padding-top: 5px;}

    /* --- 區域 B: 拉霸機 (變數區) --- */
    .slot-machine-casing {
        background: linear-gradient(135deg, #1a1a1a 0%, #050505 100%);
        border: 4px solid #ffd700; border-radius: 20px; padding: 15px;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2), inset 0 0 40px #000;
        position: relative;
    }
    .machine-title { 
        color: #ffeb3b; font-weight: 900; font-size: 1.8em; 
        text-align: center; margin-bottom: 15px; font-style: italic; 
        text-shadow: 0 0 8px #ff0000; letter-spacing: 1px;
    }
    
    .reel-window { 
        background: #000; border: 2px solid #333; border-radius: 10px; 
        margin-bottom: 10px; padding: 10px 2px; 
    }
    .reel-label { 
        font-size: 0.75em; color: #00e5ff; font-weight: bold; 
        text-align: center; margin-bottom: 5px; text-transform: uppercase; 
    }

    /* --- 關鍵修復：球體防亂碼 (Anti-Garble) --- */
    .ball-container { 
        display: flex; justify-content: center; gap: 4px; 
        width: 100%; flex-wrap: nowrap; /* 禁止換行 */
    }
    .ball {
        width: 34px; height: 34px; 
        min-width: 32px; /* 鎖死最小寬度 */
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #fff, #bbb);
        color: #000; font-weight: 900; font-size: 14px; /* 固定字體 */
        display: flex; align-items: center; justify-content: center;
        border: 1.5px solid #000; flex-shrink: 0; /* 禁止擠壓 */
    }
    .ball.special { background: radial-gradient(circle at 30% 30%, #ff3333, #990000); color: white; border: 1.5px solid #ffaaaa; }
    
    .scratch-num { 
        font-size: 1.8em; font-weight: 900; color: #ffd700; 
        text-align: center; letter-spacing: 8px; text-shadow: 0 0 10px #ff9900;
    }

    /* SPIN 按鈕 */
    div.stButton > button {
        width: 90px !important; height: 90px !important; border-radius: 50% !important;
        background: radial-gradient(circle at 30% 30%, #ff4444, #990000) !important;
        border: 4px solid #cc0000 !important; color: white !important; font-weight: bold !important;
        font-size: 1.2em !important; box-shadow: 0 6px 0 #550000, 0 10px 15px rgba(0,0,0,0.5) !important;
        margin: 10px auto !important; display: block !important;
    }
    div.stButton > button:active {
        transform: translateY(6px) !important; box-shadow: 0 0 0 #550000 !important;
    }
    
    /* 隱藏 Streamlit 預設 */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 手機版極限調整 */
    @media only screen and (max-width: 380px) {
        .ball { width: 30px; height: 30px; min-width: 30px; font-size: 12px; }
        .machine-title { font-size: 1.5em; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 基礎命理函式庫 (Base Logic)
# ==========================================

def get_zodiac(year):
    zods = ["🐵", "🐔", "🐶", "🐷", "🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑"]
    return zods[year % 12]

def get_constellation(month, day):
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    consts = ["♑", "♒", "♓", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐"]
    return consts[month-1] if day < dates[month-1] else consts[month]

def get_element_by_year(year):
    # 天干五行對應 (0,1金 | 2,3水 | 4,5木 | 6,7火 | 8,9土)
    last = year % 10
    mapping = {0:"金", 1:"金", 2:"水", 3:"水", 4:"木", 5:"木", 6:"火", 7:"火", 8:"土", 9:"土"}
    return mapping.get(last, "未知")

# 五行幸運尾數 (TINO 核心參數)
element_tails = { 
    "金": [4,9,0,5], 
    "木": [3,8,1,6], 
    "水": [1,6,4,9], 
    "火": [2,7,3,8], 
    "土": [0,5,2,7] 
}

# ==========================================
# 4. 定數運算引擎 (Fixed Fate Engine)
# ==========================================
# 鎖定條件：姓名 + 生日 + 當天日期 (同一天內按幾次都不變)

def generate_fixed_fate(name, dob, today_str):
    # 建立日基底種子 (Day Seed)
    raw_str = f"{name}_{dob}_{today_str}"
    day_seed = int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)
    
    random.seed(day_seed)
    
    # 1. 天干地支計算
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    gan_idx = (dob.year - 4) % 10
    zhi_idx = (dob.year - 4) % 12
    ganzhi = f"{gan_list[gan_idx]}{zhi_list[zhi_idx]}"
    
    # 2. 紫微主星 (14主星庫)
    ziwei_stars = [
        ("紫微星", "帝王降臨，氣場強大"), ("天機星", "智謀百出，靈感湧現"),
        ("太陽星", "光芒萬丈，正財旺盛"), ("武曲星", "剛毅果決，財庫穩固"),
        ("天同星", "福星高照，坐享其成"), ("廉貞星", "公關之神，人脈帶財"),
        ("天府星", "庫房充盈，穩健獲利"), ("太陰星", "財運如水，細水長流"),
        ("貪狼星", "慾望之主，偏財爆發"), ("巨門星", "深思熟慮，暗財湧動"),
        ("天相星", "輔佐得力，合資大吉"), ("天梁星", "逢凶化吉，必有後福"),
        ("七殺星", "將軍出征，單點突破"), ("破軍星", "先破後立，奇蹟發生")
    ]
    my_star = ziwei_stars[day_seed % 14]
    
    # 3. 姓名靈動 (Name Hash Analysis)
    name_analysis = [
        "外圓內方，領袖格局，今日決策精準。",
        "財庫飽滿，直覺敏銳，適合大膽佈局。",
        "五行相生，貴人顯現，順勢而為即可。",
        "氣場強大，突破重圍，意外之喜降臨。",
        "穩紮穩打，積沙成塔，正財運勢極佳。"
    ]
    name_result = name_analysis[day_seed % len(name_analysis)]
    
    # 4. 五行雷達數值 (本命加權)
    elements = ['金', '木', '水', '火', '土']
    r_vals = [random.randint(40, 75) for _ in range(5)]
    # 找出本命屬性索引並強化
    elem_char = get_element_by_year(dob.year)
    if elem_char in elements:
        idx = elements.index(elem_char)
        r_vals[idx] = 95 # 本命能量鎖定 95
        
    return {
        'ganzhi': ganzhi,
        'star': my_star,
        'name_res': name_result,
        'r_labs': elements,
        'r_vals': r_vals,
        'elem': elem_char
    }

# ==========================================
# 5. 變數運算引擎 (Variable Chance Engine)
# ==========================================
# 鎖定條件：微秒級時間戳 (每次按都不一樣)

def check_smart_filters(numbers):
    """
    TINO 生存協議 (Survival Protocol)
    過濾掉「必死」的號碼組合，提高分獎期望值
    """
    # 規則 1: 1-31 號過度集中 (生日牌)
    if sum(1 for n in numbers if n <= 31) > 4: return False
    
    # 規則 2: 規律連號 (如 1,2,3,4)
    sn = sorted(numbers)
    consecutive_sets = sum(1 for i in range(len(sn)-1) if sn[i+1] == sn[i]+1)
    if consecutive_sets > 2: return False
    
    # 規則 3: 極小號區 (全部 < 25)
    if all(n < 25 for n in sn): return False
    
    # 規則 4: 等差數列 (人工痕跡)
    diffs = [sn[i+1]-sn[i] for i in range(len(sn)-1)]
    if len(set(diffs)) == 1: return False
    
    return True

def generate_tino_numbers(lucky_digits, seed):
    """
    三層選號架構：五行錨點 -> 隨機填充 -> 博弈過濾
    """
    random.seed(seed)
    
    # --- 大樂透 (6+1) ---
    final_l = []
    # 嘗試 300 次以通過過濾器
    for _ in range(300):
        # Layer 1: 五行尾數 2 顆
        pool_1 = [n for n in range(1, 50) if n % 10 in lucky_digits]
        l1 = random.sample(pool_1, 2)
        # Layer 2: 隨機補滿
        pool_2 = [n for n in range(1, 50) if n not in l1]
        l2 = random.sample(pool_2, 4)
        temp_set = l1 + l2
        # Layer 3: 過濾
        if check_smart_filters(temp_set):
            final_l = sorted(temp_set)
            break
    if not final_l: final_l = sorted(temp_set) # Fallback
    
    # 特別號 (獨立事件)
    l_spec = random.choice([x for x in range(1, 50) if x not in final_l])
    
    # --- 威力彩 (6+1) ---
    # 第一區 (1-38)
    s_main = sorted(random.sample(range(1, 39), 6)) # 威力彩採純隨機+直覺
    s_spec = random.randint(1, 8)
    
    # --- 刮刮樂 (3碼) ---
    # 邏輯：2 顆五行幸運數 + 1 顆時間流秒數
    t_pool = [n for n in lucky_digits]
    t_nums = random.sample(t_pool, 2)
    t_nums.append(int(datetime.now().strftime("%S")) % 10)
    random.shuffle(t_nums)
    
    return final_l, l_spec, s_main, s_spec, t_nums

# ==========================================
# 6. APP 主程序流程
# ==========================================

st.markdown("<h2 style='text-align:center; color:#ffd700; margin-bottom:20px;'>🎱 Tino Lucky Ball</h2>", unsafe_allow_html=True)

# 輸入區 (預設為空)
c1, c2 = st.columns(2)
with c1: 
    u_name = st.text_input("玩家姓名", value="", placeholder="請輸入姓名")
with c2: 
    u_dob = st.date_input("生日", value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date(2030, 12, 31))

# 按鈕區 (獨立 Row)
col_btn = st.columns([1, 1, 1])[1]
with col_btn: 
    spin = st.button("SPIN")

# 邏輯觸發
if spin:
    if not u_name:
        st.warning("⚠️ 請輸入姓名以啟動演算")
    else:
        # 彩蛋：未來人
        if u_dob > date.today():
            st.toast("🛸 偵測到時空旅人訊號...", icon="👽")
            
        # 1. 取得時間參數
        today_str = date.today().strftime("%Y%m%d")
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. 計算定數 (命盤) - 傳入 today_str 確保整天不變
        fate_data = generate_fixed_fate(u_name, u_dob, today_str)
        
        # 3. 計算變數 (號碼) - 傳入微秒 seed 確保每次變動
        micro_seed = int(hashlib.sha256(f"{u_name}{datetime.now()}".encode()).hexdigest(), 16)
        tails = element_tails.get(fate_data['elem'], [1,6]) # 根據本命取尾數
        
        l_res, ls_res, s_res, ss_res, t_res = generate_tino_numbers(tails, micro_seed)
        
        # 4. 存入 Session
        st.session_state['last_result'] = {
            'fate': fate_data,
            'l': l_res, 'ls': ls_res,
            's': s_res, 'ss': ss_res,
            't': t_res,
            'ts': now_ts,
            'zod': get_zodiac(u_dob.year),
            'const': get_constellation(u_dob.month, u_dob.day)
        }
        
        # 5. 假動畫 (增加儀式感)
        ph = st.empty()
        for _ in range(4):
             ph.markdown(f"""<div class="slot-machine-casing" style="opacity:0.7; text-align:center;"><h2 style="color:#ffd700;">CALCULATING...</h2></div>""", unsafe_allow_html=True)
             time.sleep(0.1)
        ph.empty()

# ==========================================
# 7. 結果渲染 (View Layer)
# ==========================================

if st.session_state['last_result']:
    res = st.session_state['last_result']
    f = res['fate']
    
    # --- A. 命理戰報區 (並排顯示) ---
    st.markdown(f"""
    <div class="fate-container">
        <div class="fate-header">🌌 命盤與運勢推演 ({u_name})</div>
    """, unsafe_allow_html=True)
    
    # 使用 columns 將文字與雷達圖分開
    col_txt, col_radar = st.columns([1.3, 1])
    
    with col_txt:
        st.markdown(f"""
        <div class="fate-text">
            <span class="highlight">【先天】</span> {f['ganzhi']}年 ({res['zod']})，屬{f['elem']}。<br>
            <span class="highlight">【主星】</span> <strong>{f['star'][0]}</strong><br>
            <span style="color:#aaa; font-size:0.9em;">_{f['star'][1]}_</span><br>
            <span class="highlight">【靈動】</span> {f['name_res']}
        </div>
        """, unsafe_allow_html=True)
        
    with col_radar:
        # 繪製雷達圖
        fig = go.Figure(data=go.Scatterpolar(
            r=f['r_vals'] + [f['r_vals'][0]], 
            theta=f['r_labs'] + [f['r_labs'][0]], 
            fill='toself', 
            line_color='#00e5ff', 
            fillcolor='rgba(0, 229, 255, 0.2)',
            marker=dict(size=4)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100]),
                angularaxis=dict(tickfont=dict(size=10, color='#aaa'), rotation=90, direction='clockwise'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=140
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown(f"""
        <div class="timestamp">演算日期：{date.today()} | 觸發時間：{res['ts']}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- B. 拉霸機開獎區 ---
    st.markdown(f"""
    <div class="slot-machine-casing">
        <div class="machine-title">TINO LUCKY BALL</div>
        
        <div class="reel-window">
            <div class="reel-label">大樂透 LOTTO</div>
            <div class="ball-container">
                {"".join([f'<div class="ball">{n:02d}</div>' for n in res['l']])}
                <div class="ball special">{res['ls']:02d}</div>
            </div>
        </div>
        
        <div class="reel-window">
            <div class="reel-label">威力彩 SUPER</div>
            <div class="ball-container">
                {"".join([f'<div class="ball">{n:02d}</div>' for n in res['s']])}
                <div class="ball special">{res['ss']:02d}</div>
            </div>
        </div>
        
        <div class="reel-window">
            <div class="reel-label">刮刮樂 SCRATCH</div>
            <div class="scratch-num">
                {res['t'][0]} &nbsp; {res['t'][1]} &nbsp; {res['t'][2]}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
