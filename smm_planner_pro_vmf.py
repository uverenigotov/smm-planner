import os
import sqlite3
import pandas as pd
import datetime
import urllib.parse
import streamlit as st

# ==========================================
# 1. DATABASE MANAGEMENT (Единая база SQLite)
# ==========================================
DB_FILE = "smm_planner.db"
STATUS_OPTIONS = ["💡 Идея", "✍️ В работе", "✅ Готов к публикации", "🚀 Опубликован"]

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
    
    c.execute("SELECT COUNT(*) FROM posts")
    if c.fetchone()[0] == 0:
        demo_posts = [
            (
                "5 проверенных способов повысить конверсию в соцсетях",
                "Telegram",
                "🛠 Полезные советы",
                (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                "✅ Готов к публикации",
                "Как превратить подписчиков в постоянных клиентов? Разбираем 5 простых и эффективных шагов: от сильного оффера до продуманного призыва к действию.",
                "#маркетинг #smm #конверсия #бизнес #продажи",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
                "SMM Эксперт",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            (
                "Запуск новой линейки продуктов: Специальное предложение",
                "VK",
                "🔥 Акции и Услуги",
                datetime.date.today().strftime("%Y-%m-%d"),
                "✍️ В работе",
                "Мы подвели итоги сезона и готовы представить вам наше главное обновление! Узнайте первыми о новых возможностях и скидках до конца недели.",
                "#анонс #акция #новинка #продвижение",
                "",
                "Контент-Менеджер",
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

def get_all_posts():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM posts ORDER BY pub_date DESC, id DESC", conn)
    conn.close()
    return df

def save_new_post(title, channel, rubric, pub_date, status, content, hashtags="", media_url="", author="SMM ИИ"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO posts (title, channel, rubric, pub_date, status, content, hashtags, media_url, author, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, channel, rubric, str(pub_date), status, content, hashtags, media_url, author, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def update_post_status(post_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE posts SET status = ? WHERE id = ?", (new_status, post_id))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

# ==========================================
# 2. CONFIGURATION & CUSTOM STYLES
# ==========================================
st.set_page_config(
    page_title="PRO SMM Planner • Universal Edition",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .header-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #3B82F6 100%);
        color: white; padding: 26px 30px; border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
        margin-bottom: 25px; border-left: 6px solid #60A5FA;
    }
    .header-banner h1 { color: #FFFFFF !important; font-size: 2.2rem; font-weight: 800; margin: 0; }
    .header-banner p { color: #94A3B8; margin-top: 6px; font-size: 1.05rem; }
    
    .badge-idea { background-color: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .badge-work { background-color: #DBEAFE; color: #1E40AF; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .badge-ready { background-color: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .badge-published { background-color: #E0E7FF; color: #3730A3; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    
    .preview-box { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); }
    .metric-card { background: white; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .metric-value { font-size: 2rem; font-weight: 800; color: #0F172A; }
    .metric-label { color: #64748B; font-size: 0.9rem; font-weight: 500; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>🚀 PRO SMM PLANNER & AI EDITOR</h1>
    <p>Универсальный центр планирования контента, AI-копирайтинга и визуального дизайна</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. NAVIGATION SIDEBAR
# ==========================================
st.sidebar.title("🧭 Навигация")
menu = st.sidebar.radio(
    "Выберите модуль:",
    [
        "📅 Календарь и Сетка", 
        "✍ PRO Редактор и AI-Генератор", 
        "📦 Архив и База Сохраненных Постов", 
        "⚙️ Настройки и Инструкция"
    ]
)

# ==========================================
# MODULE 1: КАЛЕНДАРЬ И СЕТКА ПУБЛИКАЦИЙ
# ==========================================
if menu == "📅 Календарь и Сетка":
    st.subheader("📅 Контент-Календарь и Сетка Публикаций")
    
    df = get_all_posts()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Всего публикаций</div></div>', unsafe_allow_html=True)
    with col2:
        ready_cnt = len(df[df['status'] == '✅ Готов к публикации'])
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #059669;">{ready_cnt}</div><div class="metric-label">Готовы к выходу</div></div>', unsafe_allow_html=True)
    with col3:
        pub_cnt = len(df[df['status'] == '🚀 Опубликован'])
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #2563EB;">{pub_cnt}</div><div class="metric-label">Опубликовано</div></div>', unsafe_allow_html=True)
    with col4:
        work_cnt = len(df[df['status'].isin(['💡 Идея', '✍️ В работе'])])
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #D97706;">{work_cnt}</div><div class="metric-label">Черновики и идеи</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        channels = ["Все"] + list(df['channel'].dropna().unique()) if not df.empty else ["Все"]
        selected_channel = st.selectbox("Канал / Платформа:", channels)
    with f_col2:
        statuses = ["Все"] + list(df['status'].dropna().unique()) if not df.empty else ["Все"]
        selected_status = st.selectbox("Статус поста:", statuses)
    with f_col3:
        search_kw = st.text_input("🔍 Поиск по заголовку или тексту:", "")
    
    filtered_df = df.copy()
    if not filtered_df.empty:
        if selected_channel != "Все":
            filtered_df = filtered_df[filtered_df['channel'] == selected_channel]
        if selected_status != "Все":
            filtered_df = filtered_df[filtered_df['status'] == selected_status]
        if search_kw:
            filtered_df = filtered_df[
                filtered_df['title'].str.contains(search_kw, case=False, na=False) | 
                filtered_df['content'].str.contains(search_kw, case=False, na=False)
            ]
    
    st.markdown("---")
    
    view_mode = st.radio("Режим отображения:", ["📋 Список постов (Feed View)", "📆 Календарная сетка по датам"], horizontal=True)
    
    if view_mode == "📋 Список постов (Feed View)":
        if filtered_df.empty:
            st.info("Посты не найдены по текущим фильтрам.")
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
                        if row['hashtags']:
                            st.markdown(f"*Хэштеги:* `{row['hashtags']}`")
                        if row['media_url']:
                            st.image(row['media_url'], caption="Медиафайл / Обложка", use_container_width=True)
                    
                    with c_col2:
                        st.markdown(f'<span class="{status_class}">{row["status"]}</span>', unsafe_allow_html=True)
                        st.write("")
                        
                        current_status = str(row['status'])
                        status_index = 0
                        for i, s_opt in enumerate(STATUS_OPTIONS):
                            if s_opt.strip() in current_status.strip() or current_status.strip() in s_opt.strip():
                                status_index = i
                                break
                        
                        new_st = st.selectbox(
                            "Изменить статус:", 
                            STATUS_OPTIONS, 
                            index=status_index,
                            key=f"st_change_{row['id']}"
                        )
                        
                        if new_st != row['status']:
                            update_post_status(row['id'], new_st)
                            st.success("Статус обновлен!")
                            st.rerun()
                            
                        if st.button("🗑 Удалить", key=f"del_{row['id']}"):
                            delete_post(row['id'])
                            st.success("Пост удален!")
                            st.rerun()
    else:
        st.markdown("### 🗓 Расписание публикаций по дням")
        if filtered_df.empty:
            st.info("Нет постов для отображения.")
        else:
            grouped = filtered_df.groupby('pub_date')
            for p_date, group in grouped:
                st.markdown(f"#### 📅 {p_date}")
                for _, post in group.iterrows():
                    st.info(f"**[{post['channel']}]** {post['title']} — *Статус: {post['status']}* (Рубрика: {post['rubric']})")

# ==========================================
# MODULE 2: PRO РЕДАКТОР И AI-ГЕНЕРАТОР
# ==========================================
elif menu == "✍ PRO Редактор и AI-Генератор":
    st.subheader("✍️ Профессиональный Редактор и AI-Конструктор")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🪄 Универсальный AI-Конструктор", 
        "👁 Live-Предпросмотр и Ручной Ввод", 
        "🤖 Генерация текста через Gemini AI",
        "🎨 AI-Обложки и Иллюстрации"
    ])
    
    with tab1:
        st.markdown("#### 🧩 Конструктор промптов под любой бизнес / проект")
        
        col_a, col_b = st.columns(2)
        with col_a:
            b_brand = st.text_input("Название компании / проекта / бренда:", "ЭкоМаркет", key="b_brand")
            b_channel = st.selectbox("Платформа:", ["Telegram", "VK", "Google Business Profile", "Яндекс Карты", "Instagram"], key="b_channel")
            b_rubric = st.selectbox("Рубрика:", ["🛠 Полезные советы", "🔥 Акции и Скидки", "⭐ Кейсы и Отзывы", "💡 Обзор продукта", "🚀 Новости компании"], key="b_rubric")
            b_pain = st.text_area("Проблема / Боль целевой аудитории:", "Нехватка времени на приготовление полезной и здоровой еды дома.", key="b_pain")
            
        with col_b:
            b_solution = st.text_area("Ваше решение / Продукт:", "Готовые наборы полезных рационов с доставкой за 30 минут.", key="b_solution")
            b_tone = st.selectbox("Тональность (Tone of Voice):", ["Экспертная и убедительная", "Дружелюбная и заботливая", "Энергичная и продающая", "Лаконичная и деловая"], key="b_tone")
            b_cta = st.text_input("Призыв к действию (CTA):", "Закажите пробный набор со скидкой 20% по ссылке в профиле!", key="b_cta")
            b_author = st.text_input("Автор поста:", "Команда бренда", key="b_author")

        generated_prompt = f"""Ты — высококлассный SMM-копирайтер. Напиши профессиональный пост для платформы {b_channel}.
Проект / Бренд: «{b_brand}».
Рубрика: {b_rubric}.
Тональность: {b_tone}.

Структура поста:
1. Завлекающий заголовок, попадающий в боль аудитории: "{b_pain}"
2. Понятное и эффективное решение: "{b_solution}"
3. Основные преимущества и польза для читателя.
4. Четкий призыв к действию (CTA): "{b_cta}"
5. Подберите 3-5 релевантных хэштегов."""

        st.markdown("##### 🚀 Сформированный промпт для нейросети:")
        st.code(generated_prompt, language="text")

    with tab2:
        st.markdown("#### ✏️ Ручное редактирование и моментальный предпросмотр")
        
        e_col1, e_col2 = st.columns([1.1, 0.9])
        
        with e_col1:
            edit_title = st.text_input("Заголовок поста:", "Как начать питаться правильно без лишних затрат времени?", key="edit_title")
            
            c_row1, c_row2 = st.columns(2)
            with c_row1:
                edit_channel = st.selectbox("Платформа:", ["Telegram", "VK", "Google Business Profile", "Яндекс Карты"], index=0, key="edit_channel")
                edit_rubric = st.selectbox("Рубрика:", ["🛠 Полезные советы", "🔥 Акции и Услуги", "⭐ Кейсы и Истории"], index=0, key="edit_rubric")
            with c_row2:
                edit_date = st.date_input("Дата публикации:", datetime.date.today() + datetime.timedelta(days=1), key="edit_date")
                edit_status = st.selectbox("Статус:", STATUS_OPTIONS, index=2, key="edit_status")
            
            edit_content = st.text_area("Текст поста:", 
                "🥗 Правильное питание — это не сложно, если подход к нему системный!\n\n"
                "Многие считают, что ЗОЖ требует часов стояния у плиты. Но главный секрет заключается в правильном планировании меню на неделю вперед.\n\n"
                "Вот 3 простых правила:\n"
                "1️⃣ Готовьте базовые ингредиенты заранее.\n"
                "2️⃣ Используйте замороженные овощные смеси.\n"
                "3️⃣ Доверьте доставку рационов профессионалам.\n\n"
                "👉 Переходите на наш сайт и получите скидку на первый заказ!", height=200, key="edit_content")
            
            edit_tags = st.text_input("Хэштеги:", "#зож #правильноепитание #продуктивность #здоровье", key="edit_tags")
            edit_media = st.text_input("Ссылка на медиа/фото:", "https://images.unsplash.com/photo-1498837167922-ddd27525d352", key="edit_media")
            edit_author_name = st.text_input("Автор:", "SMM Менеджер", key="edit_author_name")
            
            if st.button("💾 Сохранить пост в Базу Данных", type="primary", key="save_manual_post"):
                save_new_post(edit_title, edit_channel, edit_rubric, edit_date, edit_status, edit_content, edit_tags, edit_media, edit_author_name)
                st.balloons()
                st.success("🎉 Пост успешно сохранен!")

        with e_col2:
            st.markdown("##### 👁 Предпросмотр публикации")
            st.markdown(f"""
            <div class="preview-box">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
                    <div style="background-color: #3B82F6; color: white; width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.1rem;">SMM</div>
                    <div>
                        <div style="font-weight: 700; color: #0F172A;">{edit_author_name}</div>
                        <div style="font-size: 0.8rem; color: #64748B;">{edit_channel} • {edit_date}</div>
                    </div>
                </div>
                <h4 style="margin-top: 0; color: #0F172A; font-size: 1.1rem;">{edit_title}</h4>
                <p style="white-space: pre-wrap; font-size: 0.95rem; line-height: 1.5; color: #334155;">{edit_content}</p>
                <div style="color: #2563EB; font-size: 0.85rem; font-weight: 600; margin-top: 12px;">{edit_tags}</div>
            </div>
            """, unsafe_allow_html=True)
            if edit_media:
                st.image(edit_media, caption="Предпросмотр прикреплённого изображения", use_container_width=True)

    with tab3:
        st.subheader("🤖 Генерация постов через Gemini AI API")

        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"].strip()
            st.success("✅ Gemini API Key подключен из Secrets!")
        else:
            api_key = st.text_input("🔑 Введите Ваш Gemini API Key:", type="password", key="gemini_key_input").strip()

        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Тема поста или инфоповод:", placeholder="Например: Запуск новой акции для новых клиентов", key="ai_topic")
            platform = st.selectbox("Платформа:", ["Telegram", "VK", "Google Business Profile", "Яндекс Карты"], key="ai_platform")
        with col2:
            tone = st.selectbox("Тон публикации:", ["Вовлекающий и полезный", "Продающий и убедительный", "Деловой и экспертный"], key="ai_tone")
            include_cta = st.checkbox("Добавить призыв к действию и контакты", value=True, key="ai_cta")

        if st.button("🚀 Сгенерировать пост", type="primary", key="ai_gen_btn"):
            if not topic.strip():
                st.warning("Пожалуйста, укажите тему поста.")
            elif not api_key:
                st.error("Пожалуйста, укажите Gemini API Key.")
            else:
                with st.spinner("Запрос к Google API и генерация текста..."):
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        
                        prompt = f"""Ты — профессиональный SMM-копирайтер. Напиши готовый к публикации пост на РУССКОМ языке для {platform}.

Тема поста: {topic}
Тональность: {tone}

ТРЕБОВАНИЯ:
1. Напиши ТОЛЬКО готовый текст поста на русском языке.
2. Используй стильное форматирование, эмодзи и абзацы.
"""
                        if include_cta:
                            prompt += "\n3. В конце добавь сильный призыв к действию и предложение обратиться в компанию."

                        available_models = []
                        try:
                            for m in genai.list_models():
                                if 'generateContent' in m.supported_generation_methods:
                                    clean_name = m.name.replace("models/", "")
                                    available_models.append(clean_name)
                        except Exception:
                            pass

                        priority_list = [
                            "gemini-2.5-flash",
                            "gemini-2.0-flash",
                            "gemini-1.5-flash-latest",
                            "gemini-1.5-flash",
                            "gemini-1.5-pro",
                            "gemini-pro"
                        ]

                        candidates = [m for m in priority_list if m in available_models] + available_models + priority_list
                        candidates = list(dict.fromkeys(candidates))

                        response = None
                        used_model = None
                        last_error = None

                        for model_name in candidates:
                            try:
                                model = genai.GenerativeModel(model_name)
                                res = model.generate_content(prompt)
                                if res and res.text:
                                    response = res
                                    used_model = model_name
                                    break
                            except Exception as err:
                                last_error = err
                                continue

                        if response and response.text:
                            st.session_state["current_ai_text"] = response.text
                            st.session_state["current_ai_model"] = used_model
                            st.session_state["last_gen_topic"] = topic
                            st.session_state["last_gen_platform"] = platform
                            st.session_state["last_gen_tone"] = tone
                        else:
                            st.error(f"⚠️ Ошибка API: {last_error}")

                    except Exception as e:
                        st.error(f"⚠️ Ошибка подключения к Google API: {e}")

        if "current_ai_text" in st.session_state and st.session_state["current_ai_text"]:
            st.success(f"🎉 Сгенерировано (Использована модель: `{st.session_state.get('current_ai_model', 'Gemini')}`)!")
            
            final_text = st.text_area("Результат:", value=st.session_state["current_ai_text"], height=250, key="ai_result_output")
            st.session_state["current_ai_text"] = final_text

            if st.button("💾 Сохранить пост в Календарь и Базу", type="primary", key="save_ai_post_btn"):
                saved_topic = st.session_state.get("last_gen_topic", "Сгенерированный пост")
                saved_platform = st.session_state.get("last_gen_platform", "Telegram")
                saved_tone = st.session_state.get("last_gen_tone", "🛠 Полезные советы")
                today_str = datetime.date.today().strftime("%Y-%m-%d")

                save_new_post(
                    title=saved_topic,
                    channel=saved_platform,
                    rubric=saved_tone,
                    pub_date=today_str,
                    status="✅ Готов к публикации",
                    content=final_text,
                    hashtags="#smm #контент #продвижение",
                    author="Gemini AI"
                )
                st.balloons()
                st.success("✅ Пост записан в базу данных!")

    # ==========================================
    # TAB 4: AI-ГЕНЕРАЦИЯ ОБЛОЖЕК И ИЛЛЮСТРАЦИЙ
    # ==========================================
    with tab4:
        st.subheader("🎨 Генерация обложек и иллюстраций для постов")
        st.markdown("Создавайте сочные обложки под ваш контент по текстовому описанию.")

        img_col1, img_col2 = st.columns([1.1, 0.9])

        with img_col1:
            img_prompt = st.text_area(
                "Опишите картинку (Промпт):", 
                "Современный минималистичный баннер для соцсетей: правильное здоровое питание, свежие овощи, фрукты, светлый фон, 8k качество",
                height=110,
                key="img_gen_prompt"
            )

            style_preset = st.selectbox(
                "Стиль изображения:",
                ["Photorealistic (Реалистичное фото)", "Digital Art (Цифровая графика)", "Minimalist (Минимализм)", "3D Render (3D Моделирование)"],
                key="img_style"
            )

            gen_method = st.radio("Режим генерации:", ["⚡ Быстрый генератор (Instant AI)", "🎯 Imagen 3 (Google Gemini API)"], horizontal=True)

            if st.button("🖼 Сгенерировать обложку", type="primary", key="start_img_gen"):
                full_prompt = f"{img_prompt}, {style_preset.split(' ')[0]} style, high resolution, studio lighting"
                
                if gen_method == "🎯 Imagen 3 (Google Gemini API)":
                    with st.spinner("Генерация изображения через Imagen 3..."):
                        try:
                            import google.generativeai as genai
                            if "GEMINI_API_KEY" in st.secrets:
                                genai.configure(api_key=st.secrets["GEMINI_API_KEY"].strip())
                            
                            imagen = genai.ImageGenerationModel("imagen-3.0-generate-002")
                            result = imagen.generate_images(prompt=full_prompt, number_of_images=1)
                            
                            if result and result.images:
                                image_bytes = result.images[0]._image_bytes
                                st.session_state["generated_img_url"] = None
                                st.session_state["generated_img_bytes"] = image_bytes
                                st.success("🎉 Картинка успешно сгенерирована!")
                        except Exception as e:
                            st.warning(f"Imagen 3 недоступен на вашем тарифном ключе ({e}). Переключаем на Instant AI...")
                            encoded = urllib.parse.quote(full_prompt)
                            st.session_state["generated_img_url"] = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                            st.session_state["generated_img_bytes"] = None
                else:
                    encoded = urllib.parse.quote(full_prompt)
                    st.session_state["generated_img_url"] = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                    st.session_state["generated_img_bytes"] = None
                    st.success("🎉 Изображение готово!")

        with img_col2:
            st.markdown("##### 👁 Сгенерированное изображение")
            if "generated_img_bytes" in st.session_state and st.session_state["generated_img_bytes"]:
                st.image(st.session_state["generated_img_bytes"], caption="Сгенерировано via Imagen 3", use_container_width=True)
            elif "generated_img_url" in st.session_state and st.session_state["generated_img_url"]:
                st.image(st.session_state["generated_img_url"], caption="Сгенерировано via Instant AI", use_container_width=True)
                st.code(st.session_state["generated_img_url"], language="text")
                st.caption("Скопируйте эту ссылку в поле 'Ссылка на медиа' при сохранении поста.")
            else:
                st.info("Нажмите кнопку «Сгенерировать обложку», чтобы увидеть результат.")

# ==========================================
# MODULE 3: АРХИВ И БАЗА СОХРАНЕННЫХ ПОСТОВ
# ==========================================
elif menu == "📦 Архив и База Сохраненных Постов":
    st.subheader("📦 Единая База и Архив Сохраненных Постов")
    
    df = get_all_posts()
    
    if df.empty:
        st.warning("База данных пока пуста.")
    else:
        st.dataframe(
            df[['id', 'pub_date', 'channel', 'title', 'rubric', 'status', 'author', 'created_at']],
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("#### 📥 Экспорт базы публикаций")
        
        c1, c2 = st.columns(2)
        with c1:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Скачать базу в CSV",
                data=csv_data,
                file_name=f"smm_posts_export_{datetime.date.today()}.csv",
                mime="text/csv"
            )
        with c2:
            json_data = df.to_json(orient="records", force_ascii=False)
            st.download_button(
                label="📦 Скачать базу в JSON",
                data=json_data,
                file_name=f"smm_posts_export_{datetime.date.today()}.json",
                mime="application/json"
            )

# ==========================================
# MODULE 4: НАСТРОЙКИ И ИНСТРУКЦИЯ
# ==========================================
elif menu == "⚙️ Настройки и Инструкция":
    st.subheader("⚙ Управление и Инструкция")
    st.markdown("""
    Приложение работает на единой базе данных **SQLite (`smm_planner.db`)**.
    
    В настройках Streamlit Community Cloud добавьте ваш ключ в **Secrets**:
    ```toml
    GEMINI_API_KEY = "ваш_ключ"
    ```
    """)
