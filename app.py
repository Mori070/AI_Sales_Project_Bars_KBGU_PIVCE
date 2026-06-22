import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI

# 1. Настройка страницы
st.set_page_config(page_title="Анализ продаж AI", layout="wide")
st.title("📊 Интеллектуальная система анализа бизнес-данных")

# Функция подключения к SQL
def get_data():
    conn = sqlite3.connect('sales.db')
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = get_data()

# ================= ВЫВОД ДАННЫХ И ГРАФИКОВ =================
st.header("1. Текущие показатели продаж")

# Метрики сверху
total_revenue = df['revenue'].sum()
total_qty = df['quantity'].sum()

col1, col2 = st.columns(2)
col1.metric("Общая выручка (руб.)", f"{total_revenue:,.2f}")
col2.metric("Продано товаров (шт.)", total_qty)

# Таблица данных
st.subheader("Лог продаж из базы данных SQL")
st.dataframe(df, use_container_width=True)

# График выручки по категориям (Используем встроенный график Streamlit!)
st.subheader("Аналитика выручки по категориям товаров")
category_revenue = df.groupby('category', as_index=False)['revenue'].sum()
st.bar_chart(data=category_revenue, x='category', y='revenue', color='#4AF')

# ================= ФОРМА ДОБАВЛЕНИЯ ДАННЫХ =================
st.sidebar.header("➕ Добавить продажу")
with st.sidebar.form("add_form", clear_on_submit=True):
    new_date = st.date_input("Дата")
    new_product = st.text_input("Название товара", "Планшет W")
    new_cat = st.selectbox("Категория", ["Электроника", "Аксессуары", "Одежда", "Другое"])
    new_qty = st.number_input("Количество", min_value=1, value=1)
    new_price = st.number_input("Цена за шт. (руб.)", min_value=0.0, value=10000.0)
    
    submit = st.form_submit_button("Сохранить в SQL")
    
    if submit:
        rev = new_qty * new_price
        conn = sqlite3.connect('sales.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (date, product, category, quantity, price, revenue) VALUES (?, ?, ?, ?, ?, ?)",
            (str(new_date), new_product, new_cat, new_qty, new_price, rev)
        )
        conn.commit()
        conn.close()
        st.sidebar.success("Данные успешно добавлены!")
        st.rarun() if hasattr(st, "rarun") else st.rerun()

# ================= ИНТЕГРАЦИЯ С ИИ (API) =================
# ================= ИНТЕГРАЦИЯ С ИИ (РЕАЛЬНЫЙ API) =================
st.header("🤖 ИИ-Рекомендации для принятия решений")

if st.button("Сгенерировать бизнес-рекомендации"):
    if df.empty:
        st.warning("База данных SQL пуста. Добавьте продажи, чтобы ИИ мог их проанализировать!")
    else:
        # Формируем текстовую сводку из реальных данных SQL
        summary_text = f"Общая выручка компании: {total_revenue} рублей. Всего продано товаров: {total_qty} штук. "
        summary_text += "Статистика выручки по текущим категориям товаров:\n"
        for idx, row in category_revenue.iterrows():
            summary_text += f"- {row['category']}: {row['revenue']} рублей.\n"
            
        st.info("Отправка текущих данных из SQL в нейросеть через OpenRouter API...")
        
        try:
            # Настройка подключения к бесплатному ИИ на OpenRouter
            client = OpenAI(
                base_url="https://openrouter.ai",
                api_key="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"


            )
            
            prompt = f"Ты опытный бизнес-аналитик в сфере цифровой экономики. Внимательно изучи текущие данные о продажах компании: {summary_text}. На основе этих цифр сформируй ровно 3 конкретных, точных и практичных управленческих решения на русском языке. Пиши кратко, по делу, без лишней воды."
            
            # Используем отличную бесплатную модель от Google / Meta
            response = client.chat.completions.create(
                model="google/gemma-2-9b-it:free", 
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Выводим живой ответ ИИ на экран
            st.success("Рекомендации успешно сформированы ИИ в реальном времени:")
            st.write(response.choices.message.content)
            
        except Exception as e:
            st.error(f"Ошибка подключения к API: {e}")

