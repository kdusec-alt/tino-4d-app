import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# ==========================================
# 頁面設定
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
# CSS（已包含你想要的風格）
# ==========================================
st.markdown("""
<style>
.stApp { background-color: #000; color: #f0f0f0; font-family: sans-serif; }
.block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 540px !important; }

/* 日期時間區 */
.today-info {
    text-align: center;
    color: #ffcc00;
    font-size: 1.05em;
    font-weight: bold;
    margin-bottom: 12px;
    padding: 8px;
    background: rgba(255, 204, 0, 0.1);
    border-radius: 8px;
    border: 1px solid #ffcc0066;
}

/* 命理戰報卡片 */
.fate-card {
    background: linear-gradient(180deg, #1a0505 0%, #000 100%);
    border: 2px solid #ff4444;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 16px;
    box-shadow: 0 0 16px rgba(255, 68, 68, 0.25);
}
.fate-header {
    color: #ffd700;
    font-size: 1.2em;
    font-weight: bold;
    border-bottom: 1px solid #444;
    padding-bottom: 8px;
    margin-bottom: 12px;
}
.fate-content {
    font-size: 0.95em;
    line-height: 1.6;
    color: #eee;
}
.highlight {
    color: #00e5ff;
    font-weight: bold;
}

/* 主星專屬美化 */
.main-star-box {
    margin: 12px 0;
    padding: 12px;
    background: rgba(255, 215, 0, 0.08);
    border: 1px solid #ffcc0066;
    border-radius: 8px;
}
.main-star-title {
    color: #00e5ff;
    font-size: 1.15em;
    margin-bottom: 6px;
}
.main-star-name {
    color: #ffeb3b;
    font-size: 1.5em;
    font-weight: bold;
    letter-spacing: 1px;
    display: block;
    margin: 6px 0;
}
.main-star-desc {
    color: #ffcc99;
    font-size: 1.05em;
}

/* 拉霸機外殼 */
.slot-machine {
    background: linear-gradient(135deg, #1a1a1a 0%, #050505 100%);
    border: 4px solid #ffd700;
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.2), inset 0 0 40px #000;
    margin-bottom: 24px;
}
.machine-title {
    color: #ffeb3b;
    font-weight: 900;
    font-size: 1.8em;
    text-align: center;
    margin-bottom: 16px;
    font-style: italic;
    text-shadow: 0 0 8px #ff0000;
}

/* 號碼視窗 */
.reel-box {
    background: #000;
    border: 2px solid #333;
    border-radius: 10px;
    margin-bottom: 12px;
    padding: 10px 4px;
}
.reel-label {
    font-size: 0.8em;
    color: #00e5ff;
    font-weight: bold;
    text-align: center;
    margin-bottom: 6px;
}

/* 球體 */
.ball-row {
    display: flex;
    justify-content: center;
    gap: 4px;
    width: 100%;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding: 4px 0;
}
.ball {
    width: 34px !important;
    height: 34px !important;
    min-width: 34px !important;
    border-radius: 50%;
    flex-shrink: 0;
    background: radial-gradient(circle at 30% 30%, #fff, #bbb);
    color: #000;
    font-weight: 900;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1.5px solid #000;
    box-shadow: 1px 1px 3px rgba(0,0,0,0.8);
}
.ball.special {
    background: radial-gradient(circle at 30% 30%, #ff3333, #990000);
    color: white;
    border-color: #ff9999;
}
.scratch-text {
    font-size: 2em;
    font-weight: 900;
    color: #ffd700;
    text-align: center;
    letter-spacing: 6px;
    margin-top: 8px;
}

/* 按鈕 */
div.stButton > button {
    width: 100% !important;
    border-radius: 50px !important;
    height: 52px !important;
    background: linear-gradient(180deg, #ff4444 0%, #cc0000 100%) !important;
    border: 2px solid #ffd700 !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 1.25em !important;
    margin-top: 12px !important;
}

/* 手機適配 */
@media (max-width: 480px) {
    .ball { width: 30px !important; height: 30px !important; font-size: 13px !important; }
    .ball-row { gap: 3px; padding: 3px 0; }
    .machine-title { font-size: 1.5em; }
    .scratch-text { font-size: 1.7em; letter-spacing: 4px; }
    .today-info { font-size: 0.95em; }
}

#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 核心邏輯函數（與你目前一致）
# ==========================================
def get_element_by_year(year):
    last = year % 10
    mapping = {0:"金", 1:"金", 2:"水", 3:"水", 4:"木", 5:"木", 6:"火", 7:"火", 8:"土", 9:"土"}
    return mapping.get(last, "未知")

element_tails = {
    "金": [4,9,0,5], "木": [3,8,1,6], "水": [1,6,4,9],
    "火": [2,7,3,8], "土": [0,5,2,7]
}

def calculate_fixed_fate(name, dob):
    today_str = date.today().strftime("%Y%m%d")
    fate_seed = int(hashlib.sha256(f"{name}{dob}{today_str}".encode('utf-8')).hexdigest(), 16)
    random.seed(fate_seed)
   
    gan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    zhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    ganzhi = f"{gan[(dob.year-4)%10]}{zhi[(dob.year-4)%12]}"
   
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
   
    name_analyses = [
        "外圓內方，領袖格局", "財庫飽滿，直覺敏銳", "五行相生，貴人顯現",
        "氣場強大，突破重圍", "穩紮穩打，積沙成塔", "靈光乍現，意外之喜"
    ]
    name_res = name_analyses[fate_seed % 6]
   
    elements = ['金', '木', '水', '火', '土']
    r_vals = [random.randint(40, 75) for _ in range(5)]
    elem_char = get_element_by_year(dob.year)
    if elem_char in elements:
        r_vals[elements.index(elem_char)] = 95
       
    return {
        'ganzhi': ganzhi,
        'star': my_star,
        'name_res': name_res,
        'r_labs': elements,
        'r_vals': r_vals,
        'elem': elem_char
    }

def check_filters(numbers):
    if sum(1 for n in numbers if n <= 31) > 4: return False
    sn = sorted(numbers)
    if sum(1 for i in range(len(sn)-1) if sn[i+1] == sn[i]+1) > 2: return False
    if all(n < 25 for n in sn): return False
    return True

def calculate_variable_numbers(lucky_digits):
    now_seed = int(hashlib.sha256(datetime.now().strftime("%Y%m%d%H%M%S%f").encode()).hexdigest(), 16)
    random.seed(now_seed)
   
    final_l = []
    for _ in range(300):
        l1 = random.sample([n for n in range(1, 50) if n % 10 in lucky_digits], min(2, len(lucky_digits)))
        remain = [n for n in range(1, 50) if n not in l1]
        l2 = random.sample(remain, 4)
        temp = l1 + l2
        if check_filters(temp):
            final_l = sorted(temp)
            break
    if not final_l:
        final_l = sorted(temp)
   
    l_spec = random.randint(1, 49)
    while l_spec in final_l:
        l_spec = random.randint(1, 49)
   
    s_main = sorted(random.sample(range(1, 39), 6))
    s_spec = random.randint(1, 8)
   
    t_nums = random.sample(range(10), 3)
   
    return final_l, l_spec, s_main, s_spec, t_nums

# ==========================================
# 介面
# ==========================================
st.markdown("<h2 style='text-align:center; color:#ffd700;'>🎱 Tino Lucky Ball</h2>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    u_name = st.text_input("玩家姓名", value="", placeholder="請輸入姓名")
with c2:
    u_dob = st.date_input("生日", value=date(2000, 1, 1),
                          min_value=date(1900, 1, 1), max_value=date(2030, 12, 31))

if st.button("SPIN (啟動演算)", type="primary"):
    if not u_name.strip():
        st.error("請輸入姓名")
    else:
        with st.spinner("宇宙演算中..."):
            time.sleep(1.2)
            
            fate_data = calculate_fixed_fate(u_name.strip(), u_dob)
            tails = element_tails.get(fate_data['elem'], [1,6])
            l, ls, s, ss, t = calculate_variable_numbers(tails)
            
            st.session_state['last_result'] = {
                'fate': fate_data,
                'l': l, 'ls': ls,
                's': s, 'ss': ss,
                't': t,
                'date': date.today().strftime("%Y-%m-%d"),
                'name': u_name.strip()
            }
            st.rerun()

# ==========================================
# 最終結果顯示（已修乾淨）
# ==========================================
if st.session_state.get('last_result'):
    res = st.session_state['last_result']
    f = res['fate']
    name_display = res.get('name', '玩家')

    # 日期時間（含星期）
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    today_str = now.strftime("%Y年%m月%d日")
    weekday_str = weekdays[now.weekday()]
    time_str = now.strftime("%H:%M")
    datetime_display = f"{today_str}　{weekday_str}　{time_str}"

    # 命理戰報（乾淨、無縮排）
    fate_html = f"""<div class="fate-card">
<div class="today-info">{datetime_display}</div>
<div class="fate-header">今日運勢戰報 ({name_display})</div>
<div class="fate-content">
<div style="margin-bottom:12px;">
<span class="highlight">【先天命格】</span><br>
{f.get('ganzhi', '未知')}年，屬{f.get('elem', '未知')}
</div>
<div class="main-star-box">
<span class="main-star-title">【今日主星】</span><br>
<strong class="main-star-name">{f['star'][0] if 'star' in f else '未知'}</strong>
<span class="main-star-desc">{f['star'][1] if 'star' in f else ''}</span>
</div>
<div>
<span class="highlight">【姓名靈動】</span><br>
{f.get('name_res', '無資料')}
</div>
</div>
</div>"""

    col_fate, col_radar = st.columns([1.35, 1])
    
    with col_fate:
        st.markdown(fate_html, unsafe_allow_html=True)
    
    with col_radar:
        fig = go.Figure(data=go.Scatterpolar(
            r=f['r_vals'] + [f['r_vals'][0]],
            theta=f['r_labs'] + [f['r_labs'][0]],
            fill='toself',
            line_color='#00e5ff',
            fillcolor='rgba(0, 229, 255, 0.25)',
            marker=dict(size=4)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100]),
                angularaxis=dict(tickfont=dict(size=11, color='#ddd'), rotation=90, direction='clockwise'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=200
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 拉霸機結果（靜態版）
    lotto_balls_html = "".join(f'<div class="ball">{n:02d}</div>' for n in res['l'])
    lotto_balls_html += f'<div class="ball special">{res["ls"]:02d}</div>'

    super_balls_html = "".join(f'<div class="ball">{n:02d}</div>' for n in res['s'])
    super_balls_html += f'<div class="ball special">{res["ss"]:02d}</div>'

    scratch_html = f"{res['t'][0]}&nbsp;&nbsp;{res['t'][1]}&nbsp;&nbsp;{res['t'][2]}"

    machine_html = f"""<div class="slot-machine">
<div class="machine-title">TINO LUCKY BALL</div>
<div class="reel-box">
<div class="reel-label">大樂透 LOTTO</div>
<div class="ball-row">{lotto_balls_html}</div>
</div>
<div class="reel-box">
<div class="reel-label" style="color:#00ff88;">威力彩 SUPER</div>
<div class="ball-row">{super_balls_html}</div>
</div>
<div class="reel-box">
<div class="reel-label" style="color:#ffd700;">刮刮樂 SCRATCH</div>
<div class="scratch-text">{scratch_html}</div>
</div>
</div>"""

    st.markdown(machine_html, unsafe_allow_html=True)
