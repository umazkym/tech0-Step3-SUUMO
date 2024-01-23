# 必要なライブラリをインポート
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
import time
import random
import folium
from streamlit_folium import folium_static

# データベースのパスとテーブル名の定義
DB_PATH = 'property.db'
HOUSE_TABLE = 'all_list'
USER_TABLE = 'authentication'

# SQLiteデータベースへの接続
conn = sqlite3.connect(DB_PATH)

# ページのリセット関数
def page_reset():
    st.session_state.page = 1
    st.session_state.df_userinfo = None

# ページのインクリメント関数
def page_up(df_userinfo):
    st.session_state.page += 1
    st.session_state.df_userinfo = df_userinfo
    st.experimental_rerun()

# 画像のリサイズ関数
def resize_image(url, max_width, max_height):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    aspect = min(max_width / width, max_height / height)
    new_width = int(width * aspect)
    new_height = int(height * aspect)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    st.image(resized_img)

# 地図上にマーカーを表示する関数
def AreaMarker(df, m):
    for _, r in df.iterrows():
        # マーカーのポップアップにHTMLを埋め込む
        html = f'''<strong>{r["Name"]}</strong><br>
            賃料: {r["Rent_Fee"]}<br>
            築年数: {r["Year"]}<br>
            レイアウト: {r["Layout"]}<br>
            <a href="{r["Url"]}" target="_blank">Link</a>
            '''
        folium.Marker(
            [r.Latitude, r.Longitude],
            popup=folium.Popup(html, max_width=300)
        ).add_to(m)

# ページ初期設定
if "page" not in st.session_state:
    st.session_state["page"] = 1
    st.session_state["df_userinfo"] = None

# ページ1
if st.session_state.page == 1:

    # ヘッダー
    header_left, header_right = st.columns([4, 1])
    with header_left:
        st.markdown("### 物件検索App")
    st.subheader('', divider='red')

    # ログイン/新規作成の選択メニュー
    input_left, input, input_right = st.columns([1.5, 4, 1.5])
    with input:
        selected = option_menu(
            None,
            ["ログイン", "新規作成"],
            icons=["door-open", "person-plus"],
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#E3E3E3"},
                "icon": {"color": "white", "font-size": "25px"},
                "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "red"}
            }
        )

        if selected == "ログイン":
            # ログインフォームの表示
            word = ["こんにちは", "お疲れ様です。", "ようこそ！", "(_´Д｀)ﾉ~~ｵﾂｶﾚｰ", "お帰りなさい！", "お待ちしてました！", "今日も一日頑張りましょう！"]
            st.subheader(random.choice(word))
            userid = st.text_input('ログインID', max_chars=10)
            passwd = st.text_input('パスワード', type='password', max_chars=20)
            query = f"SELECT * FROM {USER_TABLE} WHERE username == '{userid}' AND password == '{passwd}'"
            df_userinfo = pd.read_sql_query(query, conn)

            if st.button("ログイン", type="primary"):
                if not df_userinfo.empty:
                    st.success("OK")
                    time.sleep(1)
                    page_up(df_userinfo)
                else:
                    st.error("ログインIDもしくはパスワードが間違っています.")

        elif selected == "新規作成":
            # 新規作成フォームの表示
            word = ["はじめまして", "お初にお目にかかります", "ようこそ！", "IDとパスワードを入力"]
            st.subheader(random.choice(word))
            userid = st.text_input('ログインID', max_chars=10)
            passwd = st.text_input('パスワード', type='password', max_chars=20)

            if st.button("新規作成", type="primary"):
                df_userinfo = pd.DataFrame({
                    'username': [userid],
                    'password': [passwd]
                })
                # ユーザー情報をデータベースに書き込む
                with sqlite3.connect(DB_PATH) as conn:
                    df_userinfo.to_sql(USER_TABLE, conn, if_exists="append", index=False)

                time.sleep(1)
                page_up(df_userinfo)

# ページ2
if st.session_state.page == 2:

    # ヘッダー
    header_left, header_right = st.columns([4, 1])
    with header_left:
        st.markdown("### 物件検索App")
        df_userinfo = st.session_state.df_userinfo
        st.markdown(f"""ようこそ {df_userinfo.iloc[0]["username"]} さん""")

    with header_right:
        st.button("ログアウト", type="primary", on_click=page_reset)
    st.subheader('', divider='red')

    # サイドバーで検索条件を設定
    with st.sidebar:
        area = st.multiselect("エリアを選択", ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"])
        layout = st.multiselect("間取りを選択", ["ワンルーム", "1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3K", "3DK", "3LDK"])
        charge = st.slider(label="家賃を指定", min_value=0, max_value=500000, value=(0, 150000), step=10000)
        year = st.slider(label="築年数を指定", min_value=0, max_value=50, value=(0, 15))
        bt_search = st.button("検索", type="primary")

    if bt_search:
        # フィルタリングされたデータを取得
        df_filtered = []
        for i in range(len(area)):
            for j in range(len(layout)):
                query = f"SELECT * FROM {HOUSE_TABLE} WHERE Address LIKE '%{area[i]}%' AND Layout = '{layout[j]}' AND Rent_Fee >= '{charge[0]}' AND Rent_Fee <= '{charge[1]}' AND Year >= '{year[0]}' AND Year <= '{year[1]}'"
                df_temp = pd.read_sql(query, conn)
                df_filtered.append(df_temp)
        df_filtered = pd.concat(df_filtered, ignore_index=True)
        ave_rentfee = int(df_filtered['Rent_Fee'].mean())
        percent_format = []

        # 地図の表示
        m = folium.Map(location=[35.68,  139.75], zoom_start=13)
        AreaMarker(df_filtered, m)
        folium_static(m)

        for i in range(len(df_filtered)):
            # タブの表示
            tab1, tab2 = st.tabs(["基本情報", "詳細情報"])
            with tab1:
                # 写真と基本情報の表示
                photo, info = st.columns([1, 4])
                with photo:
                    resize_image(df_filtered['Floor_img'].iloc[i], max_width=130, max_height=150)

                with info:
                    with st.container():
                        st.markdown('###  :red[' + str(int(df_filtered['Rent_Fee'].iloc[i]) / 10000 ) + ']万円')
                        st.markdown(df_filtered['Station_Info1'].iloc[i])

                        percent = int(df_filtered['Rent_Fee'].iloc[i]) / ave_rentfee - 1.0
                        percent_format.append("{:.2%}".format(percent))
                        progress_value = max(min((int(df_filtered['Rent_Fee'].iloc[i]) / (2 * ave_rentfee)), 1.0),0.0)
                        st.progress(progress_value)

                        if percent > 0:
                            st.markdown(':red[物件価格は平均より' + percent_format[i] + '高いです。]')
                        elif percent < 0:
                            st.markdown(':green[物件価格は平均より' + percent_format[i] + '低いです。]')
                        else:
                            st.markdown('物件価格は平均並です。')

                    mainfee, subfee = st.columns([1, 1])
                    with mainfee:
                        st.markdown('管理費：'+str(df_filtered['Maintenance_Fee'].iloc[i] / 10000 ) + '万円  \n敷金：'+str(df_filtered['Deposit_Fee'].iloc[i] / 10000 ) + '万円  \n礼金：'+str(df_filtered['Gratuity_Fee'].iloc[i] / 10000 ) + '万円')
                    with subfee:
                        st.markdown('築年数：'+str(df_filtered['Year'].iloc[i])+'年  \n階数：'+str(df_filtered['Floor'].iloc[i])+'階  \n間取り：'+str(df_filtered['Layout'].iloc[i]))

            with tab2:
                # 写真と詳細情報の表示
                photo, info = st.columns([1, 4])
                with photo:
                    resize_image(df_filtered['Building_img'].iloc[i], max_width=130, max_height=150)
                with info:
                    with st.container():
                        st.markdown('##### ' + str(df_filtered['Name'].iloc[i]))
                        st.markdown(f"[詳細はこちら]({df_filtered['Url'].iloc[i]})")
                    data1, data2 = st.columns([1, 1])
                    with data1:
                        st.markdown(
                            str(df_filtered['Station_Info1'].iloc[i]) + '  \n' + str(df_filtered['Station_Info2'].iloc[i]) + '  \n' + str(
                                df_filtered['Station_Info3'].iloc[i]) + '  \n住所　：' + str(
                                df_filtered['Address'].iloc[i]) + '  \n築年数：' + str(df_filtered['Year'].iloc[i]) + '年  \n階数　：' + str(
                                df_filtered['Floor'].iloc[i]) + '階')
                    with data2:
                        st.markdown('賃料　：' + str(int(df_filtered['Rent_Fee'].iloc[i] / 10000)) + '万円  \n管理費：' + str(df_filtered['Maintenance_Fee'].iloc[i] / 10000) + '万円  \n敷金　：' + str(df_filtered['Deposit_Fee'].iloc[i] / 10000) + '万円  \n礼金　：' + str(df_filtered['Gratuity_Fee'].iloc[i] / 10000) + '万円  \n間取り：' + str(df_filtered['Layout'].iloc[i]) + '  \n面積　：' + str(df_filtered['Area'].iloc[i]))