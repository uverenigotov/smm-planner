import os
import sqlite3
import pandas as pd
import datetime
import json
import streamlit as st

# ==========================================
# 1. DATABASE SETUP
# ==========================================
DB_FILE = "smm_planner.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            channel TEXT,
            rubric TEXT,
            pub_date TEXT,
            status TEXT,
            content TEXT,
            hashtags TEXT,
            media_url TEXT,
            author TEXT,
            created_at TEXT
        )
    ''')
    
    # Check if empty, insert demo records for Armavirteleremont
    c.execute("SELECT COUNT(*) FROM posts")
    if c.fetchone()[0] == 0:
        demo_posts = [
            (
                "Топ-3 причины, почему мигает экран телевизора",
                "Google Business Profile",
                "🛠 Ликбез и Советы",
                (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                "💡 Идея",
                "Часто клиенты замечают мерцание экрана. В 80% случаев проблема в подсветке LED, а не в матрице. Ремонт подсветки с гарантией 12 месяцев в сервисе «Армавиртелеремонт». Задайте вопрос мастеру!",
                "#Армавиртелеремонт #РемонтТелевизоров #Армавир #РемонтПодсветки",
                "https://example.com/photo1.jpg",
                "Мастер Алексей",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            (
                "Бесплатная диагностика ТВ и забор техники на дом",
                "Telegram",
                "🔥 Акции и Услуги",
                datetime.date.today().strftime("%Y-%m-%d"),
                "✅ Готов к публикации",
                "Не нужно везти тяжелый 55-дюймовый ТВ самостоятельно! Курьер службы «Армавиртелеремонт» бережно доставит технику в мастерскую. Бесплатная диагностика при согласии на ремонт.",
                "#Армавиртелеремонт #ДоставкаТВ #АрмавирСервис",
                "https://example.com/photo2.jpg",
                "SMM Менеджер",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            (
                "Кейс: Восстановление плазмы 65\" после сказа напряжения",
                "VK",
                "⭐ Кейсы и До/После",
                (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
                "🚀 Опубликован",
                "Вчера восстановили плату питания после грозы. Клиент сэкономил 40 000 руб на покупке нового ТВ. Дали гарантию на блок 1 год.",
                "#Кейс #РемонтЭлектроники #Армавиртелеремонт",
                "https://example.com/photo3.jpg",
                "Мастер Алексей",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            )
        ]
        c.executemany('''
            INSERT INTO posts (title, channel, rubric, pub_date, status, content, hashtags, media_url, author, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', demo_posts)
        conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. STREAMLIT CONFIG & CUSTOM VMF STYLING
# ==========================================
st.set_page_config(
    page_title="PRO SMM Planner • ВМФ Стиль",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for VMF (Андреевский флаг) Theme: Navy Blue (#002147), Sky Blue (#005A9C), Clean White, Crisp Cards
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #F4F7FA;
    }
    
    /* Header VMF Style */
    .vmf-header {
        background: linear-gradient(135deg, #002147 0%, #003366 50%, #005A9C 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 33, 71, 0.25);
        border-bottom: 5px solid #005A9C;
        margin-bottom: 25px;
        position: relative;
    }
    
    .vmf-header h1 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .vmf-header p {
        color: #D0E1F9;
        margin-top: 6px;
        font-size: 1.05rem;
    }
    
    /* Status Badges */
    .badge-idea { background-color: #FFF3CD; color: #856404; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .badge-work { background-color: #CCE5FF; color: #004085; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .badge-ready { background-color: #D4EDDA; color: #155724; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .badge-published { background-color: #D1ECF1; color: #0C5460; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    
    /* Card Styles */
    .post-card {
        background-color: white;
        border-left: 5px solid #002147;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Preview Container */
    .preview-box {
        background-color: #FFFFFF;
        border: 1px solid #E0E6ED;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
        border-top: 4px solid #002147;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #002147;
    }
    .metric-label {
        color: #6C757D;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header Render
st.markdown("""
<div class="vmf-header">
    <h1>⚓ PRO SMM PLANNER & EDITOR</h1>
    <p>Профессиональный центр управления контентом • Система «Армавиртелеремонт» (ВМФ Флагман)</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR NAVIGATION & FILTERS
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/anchor.png", width=70)
st.sidebar.title("🧭 Навигация")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["📅 Календарь и Сетка", "✍️ PRO Редактор и AI-Генератор", "📦 Архив и База Сохраненных Постов", "⚙️ Настройки и Передача файла"]
)

# Helpers for DB
def get_all_posts():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM posts ORDER BY pub_date DESC", conn)
    conn.close()
    return df

def save_new_post(title, channel, rubric, pub_date, status, content, hashtags, media_url, author):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO posts (title, channel, rubric, pub_date, status, content, hashtags, media_url, author, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, channel, rubric, str(pub_date), status, content, hashtags, media_url, author, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

# ==========================================
# MODULE 1: КАЛЕНДАРЬ И СЕТКА ПУБЛИКАЦИЙ
# ==========================================
if menu == "📅 Календарь и Сетка":
    st.subheader("📅 Контент-Календарь и Планировщик Публикаций")
    
    df = get_all_posts()
    
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Всего постов</div></div>', unsafe_allow_html=True)
    with col2:
        ready_cnt = len(df[df['status'] == '✅ Готов к публикации'])
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #28A745;">{ready_cnt}</div><div class="metric-label">Готовы к публикации</div></div>', unsafe_allow_html=True)
    with col3:
        pub_cnt = len(df[df['status'] == '🚀 Опубликован'])
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #17A2B8;">{pub_cnt}</div><div class="metric-label">Опубликовано</div></div>', unsafe_allow_html=True)
    with col4:
        work_cnt = len(df[df['status'].isin(['💡 Идея', '✍️ В работе'])])
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #FFC107;">{work_cnt}</div><div class="metric-label">В разработке</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # Filter controls
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        selected_channel = st.selectbox("Платформа:", ["Все"] + list(df['channel'].unique()))
    with f_col2:
        selected_status = st.selectbox("Статус:", ["Все"] + list(df['status'].unique()))
    with f_col3:
        search_kw = st.text_input("🔍 Поиск по названию/тексту:", "")
    
    # Filter Data
    filtered_df = df.copy()
    if selected_channel != "Все":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]
    if selected_status != "Все":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if search_kw:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_kw, case=False, na=False) | filtered_df['content'].str.contains(search_kw, case=False, na=False)]
    
    st.markdown("---")
    
    # Calendar Grid / Card View
    view_mode = st.radio("Режим отображения:", ["📋 Список карточек (Feed)", "📆 Календарный сетчатый вид"], horizontal=True)
    
    if view_mode == "📋 Список карточек (Feed)":
        if filtered_df.empty:
            st.info("Посты не найдены по выбранным фильтрам.")
        else:
            for idx, row in filtered_df.iterrows():
                status_class = "badge-idea"
                if "Готов" in str(row['status']): status_class = "badge-ready"
                elif "Опубликован" in str(row['status']): status_class = "badge-published"
                elif "работе" in str(row['status']): status_class = "badge-work"
                
                with st.expander(f"📌 [{row['pub_date']}] {row['channel']} • {row['title']} ({row['status']})"):
                    c_col1, c_col2 = st.columns([3, 1])
                    with c_col1:
                        st.markdown(f"**Рубрика:** {row['rubric']} | **Автор:** {row['author']}")
                        st.markdown(f"**Текст поста:**\n\n{row['content']}")
                        st.markdown(f"*Хэштеги:* `{row['hashtags']}`")
                        if row['media_url']:
                            st.caption(f"Ссылка на медиа: {row['media_url']}")
                    with c_col2:
                        st.markdown(f'<span class="{status_class}">{row["status"]}</span>', unsafe_allow_html=True)
                        st.write("")
                        if st.button("🗑 Удалить пост", key=f"del_{row['id']}"):
                            delete_post(row['id'])
                            st.success("Пост удален!")
                            st.rerun()
    else:
        st.markdown("### 🗓 Сетка публикаций по дням")
        # Group by date
        grouped = filtered_df.groupby('pub_date')
        for p_date, group in grouped:
            st.markdown(f"#### 📅 {p_date}")
            for _, post in group.iterrows():
                st.info(f"**[{post['channel']}]** {post['title']} — *Статус: {post['status']}*")

# ==========================================
# MODULE 2: PRO РЕДАКТОР И AI-ГЕНЕРАТОР
# ==========================================
elif menu == "✍️ PRO Редактор и AI-Генератор":
    st.subheader("✍️ Профессиональный Редактор Постов + AI-Конструктор")
    
    tab1, tab2, tab3 = st.tabs(["🪄 AI-Конструктор Промптов", "👁 Live Предпросмотр и Сохранение", "🤖 Динамический Генератор"])
    
    with tab1:
        st.markdown("#### Конструктор задания для ИИ (для «Армавиртелеремонт»)")
        
        col_a, col_b = st.columns(2)
        with col_a:
            p_channel = st.selectbox("Канал публикации:", ["Google Business Profile", "Telegram", "VK", "Яндекс Карты"], key="p_channel")
            p_rubric = st.selectbox("Рубрика контента:", ["🛠 Ликбез и Советы", "🔥 Акции и Услуги", "⭐ Кейсы и До/После", "🛡 Гарантия и Надежность"], key="p_rubric")
            p_pain = st.text_area("Боль / Симптом клиента:", "Экран телевизора стал темным, но звук идет. Клиент боится, что сгорела дорогая матрица.", key="p_pain")
            p_solution = st.text_area("Решение сервиса Армавиртелеремонт:", "В 90% случаев это поломка светодиодной LED-подсветки. Меняем комплект полностью с гарантией 12 месяцев.", key="p_solution")
        
        with col_b:
            p_tone = st.selectbox("Тональность:", ["Экспертная и убедительная", "Заботливая и дружелюбная", "Динамичная акционная"], key="p_tone")
            p_cta = st.text_input("Призыв к действию (CTA):", "Бесплатная диагностика при ремонте. Позвоните мастеру прямо сейчас!", key="p_cta")
            p_guarantee = st.text_input("Гарантия и преимущество:", "Официальная гарантия 12 месяцев + выезд курьера за ТВ.", key="p_guarantee")
            p_author = st.text_input("Автор / Составитель:", "Мастер Алексей", key="p_author")
            
        generated_prompt = f"""Создай профессиональный пост для {p_channel} компании «Армавиртелеремонт» (сервис по ремонту телевизоров и электроники).
Рубрика: {p_rubric}.
Тональность: {p_tone}.

Структура поста:
1. Завлекающий заголовок, отражающий проблему: "{p_pain}"
2. Понятное техническое объяснение и решение: "{p_solution}"
3. Выгода клиента и гарантии: "{p_guarantee}"
4. Четкий призыв к действию: "{p_cta}"
5. Релевантные локальные хэштеги для г. Армавир."""

        st.markdown("##### 🚀 Сформированный Промпт для ИИ:")
        st.code(generated_prompt, language="text")
        
        st.info("💡 Вы можете скопировать этот промпт в Gemini или перейти во 3-ю вкладку для быстрой генерации!")

    with tab2:
        st.markdown("#### Редактирование, Предпросмотр и Сохранение в Базу")
        
        e_col1, e_col2 = st.columns([1, 1])
        
        with e_col1:
            st.markdown("##### ✏️ Форма редактирования поста")
            edit_title = st.text_input("Заголовок поста:", "Что делать, если пропало изображение на ТВ, но есть звук?", key="edit_title")
            edit_channel = st.selectbox("Платформа:", ["Google Business Profile", "Telegram", "VK", "Яндекс Карты"], index=0, key="edit_channel")
            edit_rubric = st.selectbox("Рубрика:", ["🛠 Ликбез и Советы", "🔥 Акции и Услуги", "⭐ Кейсы и До/После"], index=0, key="edit_rubric")
            edit_date = st.date_input("Дата публикации:", datetime.date.today() + datetime.timedelta(days=1), key="edit_date")
            edit_status = st.selectbox("Статус поста:", ["💡 Идея", "✍️ В работе", "✅ Готов к публикации", "🚀 Опубликован"], index=2, key="edit_status")
            
            edit_content = st.text_area("Полный текст поста:", 
                "📺 Пропало изображение, но звук остался? Без паники!\n\n"
                "Это одна из самых частых неисправностей современных LED-телевизоров. Многие думают, что 'сгорел экран' и пора покупать новый ТВ. Но в 9 из 10 случаев выходит из строя лишь планка светодиодной подсветки.\n\n"
                "🛠 В сервисе «Армавиртелеремонт» мы меняем подсветку на новую заводскую с гарантией 12 месяцев.\n\n"
                "🚗 Не хотите везти ТВ сами? Наш курьер аккуратно доставит технику в мастерскую и обратно!\n\n"
                "📞 Звоните нам прямо сейчас или оставляйте заявку на сайте.", height=200, key="edit_content")
            
            edit_tags = st.text_input("Хэштеги:", "#Армавиртелеремонт #РемонтТелевизоровАрмавир #РемонтПодсветки #СервисАрмавир", key="edit_tags")
            edit_media = st.text_input("Ссылка на фото/видео:", "https://armavirteleremont.ru/photos/backlight.jpg", key="edit_media")
            edit_author_name = st.text_input("Автор:", "SMM Армавиртелеремонт", key="edit_author_name")
            
            if st.button("💾 Сохранить пост в Базу Данных", type="primary", key="save_post_btn"):
                save_new_post(edit_title, edit_channel, edit_rubric, edit_date, edit_status, edit_content, edit_tags, edit_media, edit_author_name)
                st.balloons()
                st.success("🎉 Пост успешно сохранен в базу и доступен в календаре!")

        with e_col2:
            st.markdown("##### 👁 Live Предпросмотр (Симуляция в интерфейсе)")
            
            st.markdown(f"""
            <div class="preview-box">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <div style="background-color: #002147; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">АТ</div>
                    <div>
                        <div style="font-weight: bold; color: #002147;">Армавиртелеремонт</div>
                        <div style="font-size: 0.8rem; color: #6C757D;">{edit_channel} • {edit_date}</div>
                    </div>
                </div>
                <h4 style="margin-top: 0; color: #002147;">{edit_title}</h4>
                <p style="white-space: pre-wrap; font-size: 0.95rem; line-height: 1.5; color: #333;">{edit_content}</p>
                <div style="color: #005A9C; font-size: 0.85rem; font-weight: 500; margin-top: 10px;">{edit_tags}</div>
                <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #EEE;">
                    <button style="background-color: #002147; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; width: 100%;">📞 Позвонить / Записаться</button>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("🤖 Настоящий AI-Генератор постов (Gemini API)")

        # Проверяем, сохранен ли ключ в Streamlit Secrets
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ Gemini API Key подключен из настроек!")
        else:
            api_key = st.text_input(
                "🔑 Введите Ваш Gemini API Key:", 
                type="password", 
                help="Получить бесплатный ключ можно в Google AI Studio (aistudio.google.com)",
                key="gemini_key_input"
            )

        col1, col2 = st.columns(2)

        with col1:
            topic = st.text_input(
                "Тема поста или услуга:",
                placeholder="Например: Как Уверен и Готов помогает освоить нейросети?",
                key="ai_topic"
            )
            platform = st.selectbox(
                "Платформа:", ["VK", "Telegram", "Google Business Profile", "Яндекс Карты"],
                key="ai_platform"
            )

        with col2:
            tone = st.selectbox(
                "Тон публикации:",
                ["Экспертный / Полезный", "Продающий", "Вовлекающий / История"],
                key="ai_tone"
            )
            include_cta = st.checkbox("Добавить контакты и CTA (#Армавиртелеремонт)", value=True, key="ai_cta")

        if st.button("🚀 Сгенерировать пост с ИИ", type="primary", key="ai_gen_btn"):
            if not topic.strip():
                st.warning("Пожалуйста, укажите тему поста перед генерацией.")
            elif not api_key.strip():
                st.error("Пожалуйста, укажите Gemini API Key.")
            else:
                with st.spinner("Нейросеть генерирует уникальный текст..."):
                    try:
                        import google.generativeai as genai
                        
                        genai.configure(api_key=api_key)
                        
                        prompt = f"""Ты — профессиональный SMM-копирайтер. 
Напиши готовый к публикации пост на РУССКОМ языке для {platform}.

Тема поста: {topic}
Тональность: {tone}

СТРОГИЕ ТРЕБОВАНИЯ:
1. Напиши ТОЛЬКО финальный готовый текст поста на русском языке. 
2. Категорически запрещено выводить размышления, черновики, пояснения или текст на английском языке!
3. Используй красивое форматирование: абзацы, списки, эмодзи.
"""
                        if include_cta:
                            prompt += """
4. В конце поста обязательно добавь контакты:
   Мастерская #Армавиртелеремонт
   📞 Звоните: +7 (929) 850-19-93
   📍 Встреча по предварительному звонку.
"""

                        # Отбираем ТОЛЬКО оригинальные Gemini-модели (исключаем Gemma)
                        candidate_models = [
                            "gemini-2.5-flash",
                            "gemini-2.0-flash",
                            "gemini-1.5-flash",
                            "gemini-pro"
                        ]

                        try:
                            live_gemini = [
                                m.name.replace("models/", "") 
                                for m in genai.list_models() 
                                if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower()
                            ]
                            if live_gemini:
                                candidate_models = live_gemini + [m for m in candidate_models if m not in live_gemini]
                        except Exception:
                            pass

                        response = None
                        used_model = None
                        last_error = None

                        for model_name in candidate_models:
                            try:
                                model = genai.GenerativeModel(model_name)
                                response = model.generate_content(prompt)
                                if response and response.text:
                                    used_model = model_name
                                    break
                            except Exception as err:
                                last_error = err
                                continue

                        if response and response.text:
                            st.success(f"🎉 Пост успешно сгенерирован (модель: `{used_model}`)!")
                            
                            # Поле с текстом (его можно подправить вручную)
                            final_text = st.text_area(
                                "Готовый результат (можно отредактировать):",
                                value=response.text,
                                height=300,
                                key="ai_result_output"
                            )
                            
                            # Кнопка быстрой сохранения в базу
                            if st.button("💾 Сохранить пост в базу", type="secondary", key="save_ai_post_btn"):
                                if "saved_posts" not in st.session_state:
                                    st.session_state.saved_posts = []
                                
                                st.session_state.saved_posts.append({
                                    "topic": topic,
                                    "platform": platform,
                                    "text": final_text
                                })
                                st.success("✅ Пост сохранен! Вы можете найти его в разделе «База Сохраненных Постов».")
                        else:
                            st.error(f"Не удалось подключиться к Gemini: {last_error}")
# MODULE 3: АРХИВ И БАЗА СОХРАНЕННЫХ ПОСТОВ
# ==========================================
elif menu == "📦 Архив и База Сохраненных Постов":
    st.subheader("📦 Единая База и Архив Всех Сохраненных Постов")
    
    df = get_all_posts()
    
    if df.empty:
        st.warning("База данных пока пуста.")
    else:
        st.dataframe(
            df[['id', 'pub_date', 'channel', 'title', 'rubric', 'status', 'author']],
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("#### 📥 Экспорт базы сохраненных постов")
        
        c1, c2 = st.columns(2)
        with c1:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Скачать базу в CSV",
                data=csv_data,
                file_name=f"smm_posts_armavir_{datetime.date.today()}.csv",
                mime="text/csv"
            )
        with c2:
            json_data = df.to_json(orient="records", force_ascii=False)
            st.download_button(
                label="📦 Скачать базу в JSON",
                data=json_data,
                file_name=f"smm_posts_armavir_{datetime.date.today()}.json",
                mime="application/json"
            )

# ==========================================
# MODULE 4: НАСТРОЙКИ И ПЕРЕДАЧА ФАЙЛА
# ==========================================
elif menu == "⚙️ Настройки и Передача файла":
    st.subheader("⚙️ Управление и Передача Приложения Коллегам")
    
    st.markdown("""
    ### 🤝 Как передать и запустить этот SMM-планер:
    
    Данный файл представляет собой **автономное веб-приложение на Python (Streamlit)**.
    
    1. **Передача файла**: Вы можете передать файл `smm_planner_pro_vmf.py` и файл базы данных `smm_planner.db` любому сотруднику или партнеру.
    2. **Запуск в 1 клик / команду**:
       ```bash
       pip install streamlit pandas
       streamlit run smm_planner_pro_vmf.py
       ```
    3. **Облачный запуск**: Приложение можно за $0$ рублей задеплоить на **Streamlit Community Cloud** или **GitHub Pages/Render**, получив постоянную веб-ссылку для вашей команды!
    """)
    
    
    
