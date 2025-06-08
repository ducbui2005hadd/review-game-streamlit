import streamlit as st
import pandas as pd
import altair as alt

# Thiết lập giao diện
st.set_page_config(page_title="📊 Game Review Explorer", page_icon="🎮")
st.title("🎮 Game Review Explorer")
st.markdown("""
Phân tích các bài đánh giá game từ người chơi thực tế, bao gồm thời lượng chơi, nhận xét, và rating.
""")

# Load dữ liệu
@st.cache_data
def load_data():
    df = pd.read_csv("trained/sample_pred_results.csv") 
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    return df

df = load_data()

# Bộ lọc: chọn game
games = st.multiselect(
    "🎮 Chọn game để xem đánh giá:",
    options=df["title"].unique(),
    default=df["title"].unique()[:5]
)

# Bộ lọc: khoảng thời gian chơi
playtime_range = st.slider("⏱ Thời lượng chơi (giờ)", 0, int(df["playtime"].max()), (0, 500))

# Lọc dữ liệu
filtered_df = df[
    (df["title"].isin(games)) &
    (df["playtime"].between(playtime_range[0], playtime_range[1]))
]

# Hiển thị bảng dữ liệu
st.subheader("📋 Bảng dữ liệu đánh giá")
st.dataframe(filtered_df[[
    "date_posted", "title", "review", "playtime", "rating", "predicted_rating"
]], use_container_width=True)

# Biểu đồ 1: Trung bình rating & predicted rating theo game
st.subheader("📊 Biểu đồ rating thực tế và dự đoán theo game")
avg_ratings = filtered_df.groupby("title")[["rating", "predicted_rating"]].mean().reset_index()
avg_ratings = avg_ratings.melt(id_vars="title", var_name="Loại", value_name="Điểm trung bình")

bar_chart = (
    alt.Chart(avg_ratings)
    .mark_bar()
    .encode(
        x=alt.X("title:N", title="Game"),
        y=alt.Y("Điểm trung bình:Q"),
        color="Loại:N",
        tooltip=["title", "Loại", "Điểm trung bình"]
    )
    .properties(height=400)
)
st.altair_chart(bar_chart, use_container_width=True)

# Biểu đồ 2: Rating theo thời gian chơi
st.subheader("📈 Mối liên hệ giữa thời lượng chơi và rating")
scatter = (
    alt.Chart(filtered_df)
    .mark_circle(size=60)
    .encode(
        x=alt.X("playtime:Q", title="Thời gian chơi (giờ)"),
        y=alt.Y("rating:Q", title="Rating người dùng"),
        color="title:N",
        tooltip=["title", "review", "playtime", "rating", "predicted_rating"]
    )
    .interactive()
    .properties(height=400)
)
st.altair_chart(scatter, use_container_width=True)

# Tuỳ chọn xem toàn bộ đánh giá
with st.expander("📄 Xem toàn bộ nội dung đánh giá"):
    for _, row in filtered_df.iterrows():
        st.markdown(f"**🎮 {row['title']}** — {row['date_posted'].date()}")
        st.markdown(f"- ⏱ Thời gian chơi: **{row['playtime']} giờ**")
        st.markdown(f"- ⭐️ Rating thực tế: **{row['rating']}** — 🤖 Dự đoán: **{row['predicted_rating']}**")
        st.markdown(f"> {row['review']}")
        st.markdown("---")
