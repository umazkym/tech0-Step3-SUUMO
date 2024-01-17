import streamlit as st
from streamlit_option_menu import option_menu

header_left, header_right = st.columns([4, 1])
with header_left:
    st.subheader("物件検索App")
with header_right:
    st.button("ログアウト", type="primary")

st.header('', divider='blue')

# html = "<h1>こんにちは</h1>"
# st.components.v1.html("<center>" + html + "</center>")


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

with input:
    if selected == "ログイン":
        st.subheader("こんにちは")
        userid = st.text_input('ログインID',max_chars=10)
        passwd = st.text_input('パスワード', type='password', max_chars=20)
        st.button("ログイン",type="primary")


with input:
    if selected == "新規作成":
        st.subheader("初めまして")
        userid = st.text_input('ログインID',max_chars=10)
        passwd = st.text_input('パスワード', type='password', max_chars=20)
        st.button("ログイン", type="primary")