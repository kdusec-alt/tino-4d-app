import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# ==========================================
# 1. 系統核心配置
# ==========================================
st.set_page_config(
    page_title="Tino Lucky Ball", 
    page_icon="🌌", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 初始化 Session State
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# ==========================================
# 2. CSS 樣式表 (手機版防爆修正)
# ==========================================
st.markdown("""
<style>
    /* 全局設定 */
    .stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    
    /* 容器邊距優化 */
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 5rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important;
        max-width: 500px !important; 
    }

    /* --- 區域 A: 命理戰報 (定數) --- */
    .fate-container {
        background: linear-gradient(180deg, #2b0505 0%, #000 100%);
        border: 2px solid #ff4444; 
        border-radius: 12px; 
        padding: 12px;
        margin-bottom: 15px; 
        box-shadow: 0 0 15px rgba(255, 68, 68, 0.2);
    }
    .fate-header { 
        color: #ffd700; font-size: 1.1em; font-weight: bold; 
        border-bottom: 1px solid #444; padding-bottom: 5px; margin-bottom: 8px; 
    }
    .fate-content { font-size: 0.9em; line-height: 1.5; color: #ddd; }
    .highlight { color: #00e5ff; font-weight: bold; }
    .timestamp { font-size: 0.7em; color: #666; text-align: right; margin-top: 5px; border-top: 1px solid #333; padding-top: 2px;}

    /* --- 區域 B: 拉霸機 (變數) --- */
    .slot-machine-casing {
        background: linear-gradient(135deg, #1a1a1a 0%, #050505 100%);
        border: 4px solid #ffd700; border-radius: 20px; padding: 15px;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2), inset 0 0 40px #000;
        margin-bottom: 20px;
    }
    .machine-title { 
        color: #ffeb3b; font-weight: 900; font-size: 1.8em; 
        text-align: center; margin-bottom: 15px; font-style: italic; 
        text-shadow: 0 0 8px #ff0000; letter-spacing: 1px;
    }
    
    .reel-window { 
        background: #000; border: 2px solid #333; border-radius: 10px; 
        margin-bottom: 10px; padding: 8px 2px; 
    }
    .reel-label { 
        font-size: 0.75em; color: #00e5ff; font-weight: bold; 
        text-align: center; margin-bottom: 5px; text-transform: uppercase; 
    }

    /* 球體樣式 (強制不換行、不擠壓) */
    .ball-container { 
        display: flex; justify-content: center; gap: 3px; 
        width: 100%; flex-wrap: nowrap; 
    }
    .ball {
        width: 34px; height: 34px; 
        min-width: 32px; /* 關鍵：防止手機擠壓亂碼 */
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #fff, #bbb);
        color: #000; font-weight: 900; font-size: 14px; 
        display: flex; align-items: center; justify-content: center;
        border: 1.5px solid #000; flex-shrink: 0; 
    }
    .ball.special { background: radial-gradient(circle at 30% 30%, #ff3333, #990000); color: white; border: 1.5px solid #ffaaaa; }
    
    .scratch-num { 
        font-size: 1.8em; font-weight: 900; color: #ffd700; 
        text-align: center; letter-spacing: 8px; text-shadow: 0 0 10px #ff9900;
    }

    /* 按鈕樣式 */
    div.stButton > button {
        width: 100% !important; border-radius: 12px !important; height: 50px !important;
        background: linear-gradient(180deg, #ff4444 0%, #cc0000 100%) !important;
        border: 2px solid #ffd700 !important; color: white !important; font-weight: bold !important;
        font-size: 1.2em !important; box-shadow: 0 4px 0 #880000 !important;
    }
    div.stButton > button:active {
        transform: translateY(4px) !important; box-shadow: 0 0 0 #880000 !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 核心邏輯 (Logic Engine)
# ==========================================

def get_element_by_year(year):
    last = year % 10
    mapping = {0:"金", 1:"金", 2:"水", 3:"水", 4:"木", 5:"木", 6:"火", 7:"火", 8:"土", 9:"土"}
    return mapping.get(last, "未知")

element_tails = { 
    "金": [4,9,0,5], "木": [3,8,1,6], "水": [1,6,4,9], "火": [2,7,3,8], "土": [0,5,2,7] 
}

# --- A. 定數引擎 (Fate Engine) ---
# 邏輯：同一天、同一個人，算出來的命盤必須一樣
def calculate_fixed_fate(name, dob):
    # 使用 當前日期 (YYYYMMDD) 作為種子，確保整天不變
    today_str = date.today().strftime("%Y%m%d")
    fate_seed = int(hashlib.sha256(f"{name}{dob}{today_str}".encode()).hexdigest(), 16)
    
    random.seed(fate_seed)
    
    # 1. 天干地支
    gan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    zhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    gan_idx = (dob.year - 4) % 10
    zhi_idx = (dob.year - 4) % 12
    ganzhi = f"{gan[gan_idx]}{zhi[zhi_idx]}"
    
    # 2. 紫微主星 (14星)
    stars = [
        ("紫微", "帝王降臨，氣場強大"), ("天機", "智謀百出，靈感湧現"),
        ("太陽", "光芒萬丈，正財旺盛"), ("武曲", "剛毅果決，財庫穩固"),
        ("天同", "福星高照，坐享其成"), ("廉貞", "公關之神，人脈帶財"),
        ("天府", "庫房充盈，穩健獲利"), ("太陰", "財運如水，細水長流"),
        ("貪狼", "慾望之主，偏財爆發"), ("巨門", "深思熟慮，暗財湧動"),
        ("天相", "輔佐得力，合資大吉"), ("天梁", "逢凶化吉，必有後福"),
        ("七殺", "將軍出征，單點突破"), ("破軍", "先破後立，奇蹟發生")
    ]
    my_star = stars[fate_seed % 14]
    
    # 3. 姓名靈動
    name_analyses = [
        "外圓內方，領袖格局", "財庫飽滿，直覺敏銳", "五行相生，貴人顯現",
        "氣場強大，突破重圍", "穩紮穩打，積沙成塔", "靈光乍現，意外之喜"
    ]
    name_res = name_analyses[fate_seed % 6]
    
    # 4. 五行雷達
    elements = ['金', '木', '水', '火', '土']
    r_vals = [random.randint(40, 75) for _ in range(5)]
    elem_char = get_element_by_year(dob.year)
    if elem_char in elements:
        r_vals[elements.index(elem_char)] = 95 # 本命加強
        
    return {
        'ganzhi': ganzhi, 'star': my_star, 'name_res': name_res,
        'r_labs': elements, 'r_vals': r_vals, 'elem': elem_char
    }

# --- B. 變數引擎 (Chance Engine) ---
# 邏輯：每次按按鈕，時間不同，號碼必須不同 (博弈過濾)
def check_filters(numbers):
    # 過濾生日牌 (1-31號過多)
    if sum(1 for n in numbers if n <= 31) > 4: return False
    # 過濾連號
    sn = sorted(numbers)
    if sum(1 for i in range(len(sn)-1) if sn[i+1] == sn[i]+1) > 2: return False
    # 過濾全小號
    if all(n < 25 for n in sn): return False
    return True

def calculate_variable_numbers(lucky_digits):
    # 使用 微秒級時間戳 作為種子，確保每次都變
    now_seed = int(hashlib.sha256(datetime.now().strftime("%f").encode()).hexdigest(), 16)
    random.seed(now_seed)
    
    # 大樂透
    final_l = []
    for _ in range(300): # 300次嘗試過濾
        l1 = random.sample([n for n in range(1, 50) if n % 10 in lucky_digits], 2)
        l2 = random.sample([n for n in range(1, 50) if n not in l1], 4)
        temp = l1 + l2
        if check_filters(temp):
            final_l = sorted(temp)
            break
    if not final_l: final_l = sorted(temp) # 保底
    l_spec = random.randint(1, 49)
    while l_spec in final_l: l_spec = random.randint(1, 49)
    
    # 威力彩
    s_main = sorted(random.sample(range(1, 39), 6))
    s_spec = random.randint(1, 8)
    
    # 刮刮樂
    t_nums = random.sample(range(10), 3)
    
    return final_l, l_spec, s_main, s_spec, t_nums

# ==========================================
# 4. 介面流程 (View Layer)
# ==========================================

st.markdown("<h2 style='text-align:center; color:#ffd700;'>🎱 Tino Lucky Ball</h2>", unsafe_allow_html=True)

# 輸入區 (預設空白)
c1, c2 = st.columns(2)
with c1: u_name = st.text_input("玩家姓名", value="", placeholder="請輸入姓名")
with c2: u_dob = st.date_input("生日日期", value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date(2030, 12, 31))

if st.button("SPIN (啟動演算)"):
    if not u_name:
        st.warning("⚠️ 請輸入姓名")
    else:
        # 1. 取得定數 (今日運勢)
        fate_data = calculate_fixed_fate(u_name, u_dob)
        
        # 2. 取得變數 (開獎號碼)
        tails = element_tails.get(fate_data['elem'], [1,6])
        l, ls, s, ss, t = calculate_variable_numbers(tails)
        
        # 3. 存入 Session
        st.session_state['last_result'] = {
            'fate': fate_data, 'l': l, 'ls': ls, 's': s, 'ss': ss, 't': t,
            'ts': datetime.now().strftime("%H:%M:%S"),
            'date': date.today().strftime("%Y-%m-%d")
        }

# ==========================================
# 5. 結果顯示 (絕對防亂碼渲染)
# ==========================================

if st.session_state['last_result']:
    res = st.session_state['last_result']
    f = res['fate']
    
    # --- A. 命理戰報 (上方並排) ---
    # 這裡使用 HTML 變數拼接，不縮排，避免 Streamlit 誤判
    fate_html_content = f"""
    <div class="fate-container">
        <div class="fate-header">🌌 今日運勢戰報 ({u_name})</div>
        <div style="display:flex;">
            <div style="flex:1.2; padding-right:10px;">
                <div class="fate-content">
                    <span class="highlight">【先天】</span> {f['ganzhi']}年，屬{f['elem']}<br>
                    <span class="highlight">【主星】</span> {f['star'][0]}<br>
                    <span style="font-size:0.85em; color:#aaa;">_{f['star'][1]}_</span><br>
                    <span class="highlight">【靈動】</span> {f['name_res']}
                </div>
            </div>
            <div style="flex:1;">
                </div>
        </div>
        <div class="timestamp">演算日期：{res['date']} | 觸發時間：{res['ts']}</div>
    </div>
    """
    
    # 為了排版完美，我們先渲染上面的卡片結構，雷達圖用 columns 塞進去
    c_text, c_radar = st.columns([1.3, 1])
    
    with c_text:
        st.markdown(f"""
        <div class="fate-container" style="height: 180px; margin-bottom:0;">
            <div class="fate-header">🌌 命盤與運勢 ({u_name})</div>
            <div class="fate-content">
                <span class="highlight">【根基】</span> {f['ganzhi']}年 ({f['elem']})<br>
                <span class="highlight">【主星】</span> <strong>{f['star'][0]}</strong><br>
                <span style="color:#bbb; font-size:0.9em;">_{f['star'][1]}_</span><br>
                <span class="highlight">【靈動】</span> {f['name_res']}
            </div>
            <div class="timestamp">{res['date']} {res['ts']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_radar:
        fig = go.Figure(data=go.Scatterpolar(
            r=f['r_vals'] + [f['r_vals'][0]],
            theta=f['r_labs'] + [f['r_labs'][0]],
            fill='toself', line_color='#00e5ff', fillcolor='rgba(0, 229, 255, 0.2)',
            marker=dict(size=3)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=180
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- B. 拉霸機 (下方變數) ---
    # 建構球體 HTML (無縮排，確保渲染正確)
    balls_l = "".join([f'<div class="ball">{n:02d}</div>' for n in res['l']])
    balls_l += f'<div class="ball special">{res["ls"]:02d}</div>'
    
    balls_s = "".join([f'<div class="ball">{n:02d}</div>' for n in res['s']])
    balls_s += f'<div class="ball special">{res["ss"]:02d}</div>'
    
    scratch_nums = f"{res['t'][0]} &nbsp; {res['t'][1]} &nbsp; {res['t'][2]}"

    # 渲染拉霸機
    st.markdown(f"""
<div class="slot-machine-casing">
    <div class="machine-title">TINO LUCKY BALL</div>
    
    <div class="reel-window">
        <div class="reel-label">大樂透 LOTTO</div>
        <div class="ball-container">{balls_l}</div>
    </div>
    
    <div class="reel-window">
        <div class="reel-label" style="color:#00ff00;">威力彩 SUPER</div>
        <div class="ball-container">{balls_s}</div>
    </div>
    
    <div class="reel-window">
        <div class="reel-label" style="color:#ffd700;">刮刮樂 SCRATCH</div>
        <div class="scratch-num">{scratch_nums}</div>
    </div>
</div>
""", unsafe_allow_html=True)
