"""
app.py — Veggie Mood Matcher
Run: python -m streamlit run app.py
"""

import json
import streamlit as st
from PIL import Image
from classify import classify

with open("moods.json", encoding="utf-8") as f:
    MOODS = json.load(f)

MOOD_EMOJI = {
    "ecstatic": "😍",
    "happy":    "😊",
    "proud":    "😎",
    "meh":      "😐",
    "neutral":  "😑",
    "annoyed":  "😤",
    "offended": "💀",
}

st.set_page_config(
    page_title="Veggie Mood Matcher",
    page_icon="🥦",
    layout="centered",
)

st.title("🥦 Veggie Mood Matcher")
st.caption("Upload a veggie. Pick a dish. Find out if it's in the mood.")
st.divider()

source = st.radio(
    "How do you want to show your veggie?",
    ["📁 Upload a photo", "📷 Use my camera"],
    horizontal=True,
)

col1, col2 = st.columns(2)
img = None

with col1:
    if source == "📁 Upload a photo":
        uploaded = st.file_uploader("Pick a veggie photo", type=["jpg", "jpeg", "png"])
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
    else:
        cam = st.camera_input("📷 Snap your veggie")
        if cam:
            img = Image.open(cam).convert("RGB")

    if img:
        st.image(img, caption="Your veggie", use_container_width=True)

with col2:
    st.markdown("### 🍽️ What dish are you making?")
    dish = st.text_input(
        "Dish",
        placeholder="pizza, stirfry, salad, smoothie, burger...",
        label_visibility="collapsed",
    ).lower().strip()
    st.markdown(" ")
    go = st.button("🎭 Ask the veggie", type="primary", use_container_width=True)

if img and dish and go:
    with st.spinner("The veggie is thinking... 🤔"):
        veggie, confidence, raw_label = classify(img)

    st.divider()

    st.subheader(f"AI says: **{veggie.title()}**")
    st.caption(f"Confidence: {confidence:.0%}")

    veggie_data = MOODS.get(veggie)

    if not veggie_data:
        st.warning(f"😶 {veggie.title()} has no opinion yet. Add it to moods.json!")
        st.stop()

    entry = veggie_data.get(dish)
    if not entry:
        entry = {
            "score": 50,
            "mood": "neutral",
            "line": f"I don't know what '{dish}' is, but sure. I guess.",
        }

    score = entry["score"]
    mood = entry["mood"]
    line = entry["line"]
    emoji = MOOD_EMOJI.get(mood, "😐")
    veggie_emoji = veggie_data.get("emoji", "🥬")
    personality = veggie_data.get("personality", "")

    st.markdown(" ")
    st.markdown(f"## {veggie_emoji} {emoji}  Compatibility: **{score}%**")
    if personality:
        st.caption(f"_{veggie.title()} — the {personality}_")
    st.progress(score / 100)

    st.markdown(" ")
    st.markdown(f"> ### {line}")

    if score >= 90:
        st.balloons()
        st.success("🎉 A match made in culinary heaven!")
    elif score >= 70:
        st.success("😊 Yeah, this works.")
    elif score >= 40:
        st.info("😐 It'll do. Nobody's thrilled though.")
    elif score >= 20:
        st.warning("😤 This veggie is not happy about this.")
    else:
        st.error("💀 Absolutely not. The veggie has filed a complaint.")

elif img and not dish:
    st.info("👆 Now type a dish and click the button.")

elif dish and not img:
    st.info("👆 Now upload or snap a veggie photo.")
