import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# 頁面設定 - 手機優先
st.set_page_config(
    page_title="Tino Lucky Ball",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Session State
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# CSS - 極致緊湊版
st.markdown("""
<style>
/* 全局極簡 */
.stApp { background: #000; color: #eee; font-family: sans-serif; }
.block-container { padding: 0.6rem 0.8rem 2rem !important; max-width: 520px !important; }

/* 標題 */
h2 { margin: 0.4rem 0 0.8rem !important; font-size: 1.6em !important; }

/* 輸入與按鈕 */
div.row-widget.stHorizontal { margin-bottom: 0.4rem !important; }
div.stButton > button {
    height: 44px !important;
    font-size: 1.1em !important;
    margin: 0.3rem 0 !important;
    border-radius: 40px !important;
}

/* 日期時間 */
.today-info {
    text-align: center;
    font-size: 0.9em;
    color: #ffcc00;
    margin: 0.3rem 0 0.5rem;
    padding: 4px;
    background: rgba(255,204,0,0.08);
    border-radius: 6px;
}

/* 命理卡片 - 極壓縮 */
.fate-card {
    background: #0d0000;
    border: 1px solid #ff4444;
    border-radius: 8px;
    padding: 8px;
    margin: 0.5rem 0;
}
.fate-header {
    font-size: 1em;
    color: #ffd700;
    margin: 0 0 6px;
}
.fate-content {
    font-size: 0.84em;
    line-height: 1.35;
}
.highlight { color: #00e5ff; font-weight: bold; }
.main-star-name { color: #ffeb3b; font-size: 1.3em; font-weight: bold; margin: 4px 0; }
.main-star-desc { color: #ffcc99; font-size: 0.92em; }

/* 雷達圖 - 超小 */
div[data-testid="stPlotlyChart"] { margin: 0.3rem 0 !important; }

/* 樂透區 - 緊湊 + 圓球 */
.slot-machine {
    background: #0a0a0a;
    border: 2px solid #ffd700;
    border-radius: 12px;
    padding: 8px;
    margin: 0.6rem 0;
}
.machine-title {
    font-size: 1.3em;
    margin: 0 0 6px;
    text-align: center;
    color: #ffeb3b;
}
.reel-box {
    margin: 6px 0;
    padding: 6px 4px;
    border-radius: 6px;
    background: #000;
}
.reel-label {
    font-size: 0.75em;
    margin-bottom: 4px;
    text-align: center;
}
.ball-row {
    display: flex;
    justify-content: center;
    gap: 3px;
    flex-wrap: nowrap;
    overflow-x: auto;
}
.ball {
    width: 30px !important;
    height: 30px !important;
    min-width: 30px !important;
    border-radius: 50% !important;
    background: radial-gradient(#fff, #ccc);
    color: #000;
    font-weight: bold;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #333;
    flex-shrink: 0;
}
.ball.special {
    background: radial-gradient(#ff4444, #990000);
    color: white;
}
.scratch-text {
    font-size: 1.6em;
    color: #ffd700;
    text-align: center;
    letter-spacing: 4px;
    margin-top: 4px;
}

/* 手機極致壓縮 */
@media (max-width: 480px) {
    .block-container { padding: 0.5rem 0.6rem 1.5rem !important; }
    h2 { font-size: 1.4em !important; margin: 0.3rem 0 !important; }
    .fate-card { padding: 6px; margin: 0.4rem 0; }
    .fate-content { font-size: 0.8em; line-height: 1.3; }
    .main-star-name { font-size: 1.2em; }
    .ball { width: 26px !important; height: 26px !important; font-size: 11px !important; }
    .scratch-text { font-size: 1.4em; letter-spacing: 3px; }
    .reel-box { padding: 4px; margin: 4px 0; }
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 核心邏輯（保持不變）
# ==========================================
def get_element_by_year(year):
    last = year % 10
    mapping = {0:"金",1:"金",2:"水",3:"水",4:"木",5:"木",6:"火",7:"火",8:"土",9:"土"}
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
    
    elements = ['金','木','水','火','土']
    r_vals = [random.randint(40,75) for _ in range(5)]
    elem_char = get_element_by_year(dob.year)
    if elem_char in elements:
        r_vals[elements.index(elem_char)] = 95
    
    return {
        'ganzhi': ganzhi, 'star': my_star, 'name_res': name_res,
        'r_labs': elements, 'r_vals': r_vals, 'elem': elem_char
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
        l1 = random.sample([n for n in range(1,50) if n % 10 in lucky_digits], min(2,len(lucky_digits)))
        remain = [n for n in range(1,50) if n not in l1]
        l2 = random.sample(remain, 4)
        temp = l1 + l2
        if check_filters(temp):
            final_l = sorted(temp)
            break
    if not final_l: final_l = sorted(temp)
    
    l_spec = random.randint(1,49)
    while l_spec in final_l: l_spec = random.randint(1,49)
    
    s_main = sorted(random.sample(range(1,39),6))
    s_spec = random.randint(1,8)
    
    t_nums = random.sample(range(10),3)
    
    return final_l, l_spec, s_main, s_spec, t_nums

# ==========================================
# 介面 - 緊湊輸入
# ==========================================
st.markdown("<h2 style='text-align:center; color:#ffd700; margin:0.4rem 0;'>🎱 Tino Lucky Ball</h2>", unsafe_allow_html=True)

cols = st.columns([3,3])
with cols[0]:
    u_name = st.text_input("姓名", "", placeholder="請輸入姓名", label_visibility="collapsed")
with cols[1]:
    u_dob = st.date_input("生日", date(2000,1,1),
                          min_value=date(1900,1,1), max_value=date(2030,12,31),
                          label_visibility="collapsed")

if st.button("SPIN (啟動演算)", type="primary", use_container_width=True):
    if not u_name.strip():
        st.error("請輸入姓名")
    else:
        placeholder = st.empty()
        for _ in range(5):
            fake_l = sorted(random.sample(range(1,50),6))
            fake_ls = random.randint(1,49)
            fake_s = sorted(random.sample(range(1,39),6))
            fake_ss = random.randint(1,8)
            fake_t = random.sample(range(10),3)
            
            fake_l_html = "".join(f'<div class="ball">{n:02d}</div>' for n in fake_l) + f'<div class="ball special">{fake_ls:02d}</div>'
            fake_s_html = "".join(f'<div class="ball">{n:02d}</div>' for n in fake_s) + f'<div class="ball special">{fake_ss:02d}</div>'
            fake_scratch = f"{fake_t[0]} {fake_t[1]} {fake_t[2]}"
            
            anim = f"""<div class="slot-machine">
<div class="machine-title">運算中...</div>
<div class="reel-box"><div class="reel-label">大樂透 LOTTO</div><div class="ball-row">{fake_l_html}</div></div>
<div class="reel-box"><div class="reel-label" style="color:#00ff88;">威力彩 SUPER</div><div class="ball-row">{fake_s_html}</div></div>
<div class="reel-box"><div class="reel-label" style="color:#ffd700;">刮刮樂 SCRATCH</div><div class="scratch-text">{fake_scratch}</div></div>
</div>"""
            placeholder.markdown(anim, unsafe_allow_html=True)
            time.sleep(0.12)
        placeholder.empty()
        
        fate_data = calculate_fixed_fate(u_name.strip(), u_dob)
        tails = element_tails.get(fate_data['elem'], [1,6])
        l, ls, s, ss, t = calculate_variable_numbers(tails)
        
        st.session_state['last_result'] = {
            'fate': fate_data,
            'l': l, 'ls': ls,
            's': s, 'ss': ss,
            't': t,
            'name': u_name.strip()
        }
        st.rerun()

# ==========================================
# 結果顯示 - 極致一頁版
# ==========================================
if st.session_state.get('last_result'):
    res = st.session_state['last_result']
    f = res['fate']
    name_display = res.get('name', '玩家')

    # 日期時間
    now = datetime.now()
    weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    today_str = now.strftime("%Y年%m月%d日")
    weekday_str = weekdays[now.weekday()]
    time_str = now.strftime("%H:%M")
    datetime_display = f"{today_str}　{weekday_str}　{time_str}"

    # 命理戰報 - 極緊湊
    fate_html = f"""<div class="fate-card">
<div class="today-info">{datetime_display}</div>
<div class="fate-header">今日運勢 ({name_display})</div>
<div class="fate-content">
<span class="highlight">先天命格</span> {f.get('ganzhi','?')}年 屬{f.get('elem','?')}<br>
<div class="main-star-box">
<span class="main-star-title">今日主星</span><br>
<strong class="main-star-name">{f['star'][0] if 'star' in f else '?'}</strong><br>
<span class="main-star-desc">{f['star'][1] if 'star' in f else ''}</span>
</div>
<span class="highlight">姓名靈動</span><br>{f.get('name_res','無資料')}
</div>
</div>"""

    cols = st.columns([1,1])
    with cols[0]:
        st.markdown(fate_html, unsafe_allow_html=True)
    
    with cols[1]:
        fig = go.Figure(data=go.Scatterpolar(
            r=f['r_vals'] + [f['r_vals'][0]],
            theta=f['r_labs'] + [f['r_labs'][0]],
            fill='toself',
            line_color='#00e5ff',
            fillcolor='rgba(0,229,255,0.18)',
            marker=dict(size=3)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0,100]),
                angularaxis=dict(tickfont=dict(size=9,color='#aaa'), rotation=90, direction='clockwise'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=5,r=5,t=5,b=5),
            height=140
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 樂透區 - 緊湊橫排
    lotto_html = "".join(f'<div class="ball">{n:02d}</div>' for n in res['l']) + f'<div class="ball special">{res["ls"]:02d}</div>'
    super_html = "".join(f'<div class="ball">{n:02d}</div>' for n in res['s']) + f'<div class="ball special">{res["ss"]:02d}</div>'
    scratch_html = f"{res['t'][0]}&nbsp;{res['t'][1]}&nbsp;{res['t'][2]}"

    machine_html = f"""<div class="slot-machine">
<div class="machine-title">TINO LUCKY BALL</div>
<div class="reel-box">
<div class="reel-label">大樂透 LOTTO</div>
<div class="ball-row">{lotto_html}</div>
</div>
<div class="reel-box">
<div class="reel-label" style="color:#00ff88;">威力彩 SUPER</div>
<div class="ball-row">{super_html}</div>
</div>
<div class="reel-box">
<div class="reel-label" style="color:#ffd700;">刮刮樂 SCRATCH</div>
<div class="scratch-text">{scratch_html}</div>
</div>
</div>"""

    st.markdown(machine_html, unsafe_allow_html=True)
