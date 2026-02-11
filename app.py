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

# --- Session ---
if 'screenshot_mode' not in st.session_state:
    st.session_state['screenshot_mode'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None
if 'u_name' not in st.session_state:
    st.session_state['u_name'] = ""
if 'u_dob' not in st.session_state:
    st.session_state['u_dob'] = date(2000,1,1)

# ---------------- CSS 完整響應式 ----------------
st.markdown("""
<style>
.stApp { background:#000; color:#f0f0f0; font-family:-apple-system,BlinkMacSystemFont,sans-serif;}
.block-container { max-width:500px; padding-top:1rem; padding-bottom:5rem;}
@media(max-width:900px){ .block-container{max-width:95%;}}
@media(max-width:480px){
  .block-container{max-width:100%!important;padding-left:0.5rem;padding-right:0.5rem;}
  .ball{min-width:28px!important;width:28px!important;height:28px!important;font-size:13px!important;border-width:1px!important;}
  div.stButton>button{width:80px!important;height:80px!important;}
}

.slot-machine-casing{
 background:linear-gradient(135deg,#222,#0d0d0d);
 border:6px solid #ffd700;
 border-radius:20px;
 padding:15px;
 box-shadow:0 0 20px rgba(255,215,0,0.2), inset 0 0 40px #000;
 margin-bottom:20px;
}
.machine-top{
 text-align:center;
 background:#4a0000;
 border-radius:12px;
 padding:8px;
 margin-bottom:15px;
 border:2px solid #ff3333;
}
.machine-title{
 color:#ffeb3b;
 font-weight:900;
 font-size:1.4em;
}
.reel-window{
 background:#000;
 border:2px solid #444;
 border-radius:10px;
 margin-bottom:10px;
 padding:8px 2px;
}
.reel-label{font-size:0.7em;text-align:center;margin-bottom:4px;}
.reel-label.main{color:#00e5ff;}
.reel-label.super{color:#00ff00;}
.reel-label.scratch{color:#ffd700;}

.ball-container{display:flex;justify-content:center;gap:4px;}
.ball{
 min-width:34px;width:34px;height:34px;border-radius:50%;
 background:radial-gradient(circle at 30% 30%,#fff,#bbb);
 color:#000;font-weight:900;font-size:15px;
 display:flex;align-items:center;justify-content:center;
 border:2px solid #000;
}
.ball.special{
 background:radial-gradient(circle at 30% 30%,#ff3333,#990000);
 color:white;
}
.scratch-num{
 font-size:1.6em;font-weight:900;color:#ffd700;text-align:center;
}
div.stButton>button{
 width:90px!important;height:90px!important;
 border-radius:50%!important;
 background:radial-gradient(circle at 30% 30%,#ff4444,#990000)!important;
 border:4px solid #cc0000!important;
 box-shadow:0 8px 0 #550000;
 color:white!important;font-weight:bold!important;
}
.status-bar{
 display:flex;justify-content:space-between;
 background:#111;border-radius:8px;padding:6px 10px;margin-bottom:10px;
}
.status-highlight{color:#00e5ff;font-weight:bold;}
.radar-box{
 background:#111;border-radius:6px;padding:6px;margin-top:8px;
 font-size:0.85em;border:1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# ---------------- 原本核心 ----------------
def get_element_luck(year):
    last_digit=int(str(year)[-1])
    if last_digit in [0,1]: return "金",[4,9,0,5]
    if last_digit in [2,3]: return "水",[1,6,4,9]
    if last_digit in [4,5]: return "木",[3,8,1,6]
    if last_digit in [6,7]: return "火",[2,7,3,8]
    if last_digit in [8,9]: return "土",[5,0,2,7]
    return "未知",[]

def calculate_seed(name,dob):
    raw=f"{name}_{dob}_{datetime.now()}"
    return int(hashlib.sha256(raw.encode()).hexdigest(),16)

def wealth_radar(name,dob):
    today=datetime.now().strftime("%Y%m%d")
    seed=int(hashlib.sha256(f"{name}_{dob}_{today}".encode()).hexdigest(),16)
    score=seed%100+1
    if score>80: level="🔥 偏財高波動區"
    elif score>60: level="⚡ 偏財活躍區"
    elif score>40: level="🌊 平穩娛樂區"
    else: level="🪨 建議小額娛樂"
    return score,level

def cosmic_story(name,elem,seed):
    random.seed(seed)
    stars=["紫微震動","破軍翻湧","武曲聚財","天府開庫","貪狼啟動"]
    quantum=["量子場重組","機率雲坍縮","平行宇宙共振","時間軸偏移","財富態疊加"]
    return f"""
🌌 宇宙敘事報告

玩家：{name}
五行核心：{elem}
星曜狀態：{random.choice(stars)}
量子動態：{random.choice(quantum)}

今日請以娛樂心態參與，宇宙只提供隨機性。
"""

def render_balls(numbers,special=None):
    html='<div class="ball-container">'
    for n in numbers:
        html+=f'<div class="ball">{n:02d}</div>'
    if special:
        html+=f'<div class="ball special">{special:02d}</div>'
    html+='</div>'
    return html

# ---------------- UI ----------------
col1,col2=st.columns(2)
with col1:
    u_name=st.text_input("玩家姓名")
with col2:
    u_dob=st.date_input("玩家生日",value=date(2000,1,1))

spin=st.button("SPIN")

if spin and u_name:
    st.session_state['u_name']=u_name
    st.session_state['u_dob']=u_dob
    seed=calculate_seed(u_name,u_dob)

    random.seed(seed)
    lotto_main=sorted(random.sample(range(1,50),6))
    lotto_spec=random.randint(1,49)

    random.seed(seed+1)
    super_main=sorted(random.sample(range(1,39),6))
    super_spec=random.randint(1,8)

    random.seed(seed+2)
    scratch=random.sample(range(0,10),3)

    elem,_=get_element_luck(u_dob.year)

    st.session_state['last_result']={
        "lotto":lotto_main,
        "lotto_spec":lotto_spec,
        "super":super_main,
        "super_spec":super_spec,
        "scratch":scratch,
        "elem":elem,
        "seed":seed
    }

# ---------------- 顯示 ----------------
if st.session_state['last_result']:
    res=st.session_state['last_result']
    radar_score,radar_level=wealth_radar(
        st.session_state['u_name'],
        st.session_state['u_dob']
    )

    st.markdown(f"""
<div class="slot-machine-casing">
<div class="machine-top"><h1 class="machine-title">TINO COSMIC BALL</h1></div>

<div class="status-bar">
<div>五行 <span class="status-highlight">{res['elem']}</span></div>
<div>玩家 <span class="status-highlight">{st.session_state['u_name']}</span></div>
</div>

<div class="radar-box">
📡 今日偏財雷達：<b>{radar_score}/100</b>　{radar_level}
</div>

<div class="reel-window">
<div class="reel-label main">大樂透 LOTTO</div>
{render_balls(res['lotto'],res['lotto_spec'])}
</div>

<div class="reel-window">
<div class="reel-label super">威力彩 SUPER</div>
{render_balls(res['super'],res['super_spec'])}
</div>

<div class="reel-window">
<div class="reel-label scratch">刮刮樂 SCRATCH</div>
<div class="scratch-num">{res['scratch'][0]} &nbsp; {res['scratch'][1]} &nbsp; {res['scratch'][2]}</div>
</div>

</div>
""",unsafe_allow_html=True)

    with st.expander("🌌 豪華宇宙敘事"):
        st.write(cosmic_story(
            st.session_state['u_name'],
            res['elem'],
            res['seed']
        ))
