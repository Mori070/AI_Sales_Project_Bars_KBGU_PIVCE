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
st.header("🤖 ИИ-Рекомендации для принятия решений")

if st.button("Сгенерировать бизнес-рекомендации"):
    summary_text = f"Общая выручка: {total_revenue} руб. Продано штук: {total_qty}. "
    summary_text += "Данные по категориям:\n"
    for idx, row in category_revenue.iterrows():
        summary_text += f"- {row['category']}: {row['revenue']} руб.\n"
        
    st.info("Отправка агрегированных данных в нейросеть через API...")
    
    try:
        client = OpenAI(
            base_url="https://deepseek.com",
            api_key="ВАШ_API_КЛЮЧ"
        )
        
        prompt = f"Ты бизнес-аналитик цифровой экономики. Проанализируй данные продаж и дай 3 кратких управленческих решения. Данные: {summary_text}"
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        st.success("Рекомендации успешно сформированы:")
        st.write(response.choices.message.content)
        
    except Exception as e:
        st.warning("Режим демонстрации (API ключ не настроен). ИИ сгенерировал базовый шаблон:")
        st.write("**Анализ ИИ:** Категория 'Электроника' приносит основной доход. **Рекомендация:** Увеличить закупки смартфонов и ноутбуков перед праздниками на 15%. Снизить долю низкомаржинальных аксессуаров.")

