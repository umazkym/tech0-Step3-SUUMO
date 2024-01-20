import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import requests
import pandas as pd
from PIL import Image
from io import BytesIO

DB_PATH='property.db'
HOUSE_TABLE='all_list'
USER_TABLE='authentication'

conn = sqlite3.connect(DB_PATH)

# 設定
def page_reset():
    st.session_state.page=1

def page_up():
    st.session_state.page+=1

if "page" not in st.session_state:
    st.session_state["page"]=1

def resize_image(url, max_width, max_height):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    aspect = min(max_width/width, max_height/height)
    new_width = int(width*aspect)
    new_height = int(height*aspect)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    st.image(resized_img)

# ヘッダー
header_left, header_right = st.columns([4, 1])

with header_left:
    st.subheader("物件検索App")
with header_right:
    st.button("ログアウト", type="primary",on_click=page_reset)
st.header('', divider='blue')

# ページ1
if st.session_state.page==1:
    input_left, input, input_right = st.columns([1.5, 4, 1.5])

    with input:
        selected = option_menu(
            None,
            ["ログイン","新規作成"],
            icons=["door-open","person-plus"],  # Bootstrap アイコン名のリスト
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#E3E3E3"},
                "icon": {"color": "white", "font-size": "25px"},
                "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#1261B9"}
            }
        )

        if selected == "ログイン":
            st.subheader("こんにちは")
            userid = st.text_input('ログインID',max_chars=10)
            passwd = st.text_input('パスワード', type='password', max_chars=20)
            st.button("ログイン",type="primary",on_click=page_up)

        elif selected == "新規作成":
            st.subheader("初めまして")
            userid = st.text_input('ログインID',max_chars=10)
            passwd = st.text_input('パスワード', type='password', max_chars=20)

            if st.button("新規作成", type="primary"):
                df_new_user=pd.DataFrame({
                    'UserID':[userid],
                    'Password':[passwd]
                })
                # dfの内容をsqliteに書き込む
                with sqlite3.connect(DB_PATH) as conn:
                    df_new_user.to_sql(USER_TABLE, conn, if_exists="append", index=False)

# ページ2
if st.session_state.page==2:
    with st.sidebar:
        area=st.multiselect(
            "エリアを選択",
            ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区"]
        )
        layout=st.multiselect(
            "間取りを選択",
            ["ワンルーム", "1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3K", "3DK", "3LDK"]
        )
        charge=st.slider(
            label="家賃を指定",
            min_value=0,
            max_value=500000,
            value=(0,150000),
            step=10000
        )
        year=st.slider(
            label="築年数を指定",
            min_value=0,
            max_value=50,
            value=(0,15)
        )
        bt_search=st.button("検索",type="primary")
    if bt_search:
        df_filtered=[]
        st.header(area[len(area)-1])
        for i in range(len(area)):
            for j in range(len(layout)):
                query=f"SELECT * FROM {HOUSE_TABLE} WHERE Address LIKE '%{area[i]}%' AND Layout = '{layout[j]}' AND Rent_Fee >= '{charge[0]}' AND Rent_Fee <= '{charge[1]}' AND Year >= '{year[0]}' AND Year <= '{year[1]}'"
                df_temp=pd.read_sql(query, conn)
                df_filtered.append(df_temp)
        df_filtered=pd.concat(df_filtered, ignore_index=True)
        # st.dataframe(df_filtered)
        for i in range(5):
            tab1, tab2 = st.tabs(["基本情報", "詳細情報"])
            with tab1:
                photo, info = st.columns([1, 4])
                with photo:
                    st.markdown("aaa")
                    # resize_image(df_filtered['Floor_img'].iloc[i], max_width=130, max_height=150)
                    # st.image(df_filtered['Floor_img'].iloc[i], width=130)
                    # st.image("GNCG1659.jpg",width=130)
                with info:
                    st.markdown('##### '+str(df_filtered['Name'].iloc[i]))
                    st.caption(df_filtered['Address'].iloc[i])
                    mainfee, subfee = st.columns([1, 1])
                    with mainfee:
                        st.markdown('賃料：'+str(df_filtered['Rent_Fee'].iloc[i]))
                    with subfee:
                        st.markdown('管理費：'+str(df_filtered['Maintenance_Fee'].iloc[i])+'  \n敷金：'+str(df_filtered['Deposit_Fee'].iloc[i])+'  \n礼金：'+str(df_filtered['Gratuity_Fee'].iloc[i]))
            with tab2:
                photo, info = st.columns([1, 4])
                with photo:
                    st.markdown("aaa")
                    # resize_image(df_filtered['Building_img'].iloc[i], max_width=130, max_height=150)
                    # st.image(df_filtered['Floor_img'].iloc[i], width=130)
                    # st.image("GNCG1659.jpg",width=130)
                with info:
                    st.markdown('### '+str(df_filtered['Name'].iloc[i]))
                    mainfee, subfee = st.columns([1, 1])
                    with mainfee:
                        st.markdown(df_filtered['Station_Info1'].iloc[i])
                        st.markdown(df_filtered['Station_Info2'].iloc[i])
                        st.markdown(df_filtered['Station_Info3'].iloc[i])
                    with subfee:
                        st.markdown(df_filtered['Year'].iloc[i])
                        st.markdown(df_filtered['Floor'].iloc[i])
                        st.markdown(df_filtered['Layout'].iloc[i])
                        st.markdown(df_filtered['Area'].iloc[i])

# "Name" TEXT,
# "Building_img" TEXT,
# "Floor_img" TEXT,
# "Address" TEXT,
# "Station_Info1" TEXT,
# "Station_Info2" TEXT,
# "Station_Info3" TEXT,
# "Year" TEXT,
# "Max_Floor" TEXT,
# "Floor" REAL,
# "Rent_Fee" REAL,
# "Maintenance_Fee" REAL,
# "Deposit_Fee" REAL,
# "Gratuity_Fee" REAL,
# "Layout" TEXT,
# "Area" TEXT