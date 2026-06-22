import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Анализ продаж AI", layout="wide")
st.title("📊 Интеллектуальная система анализа бизнес-данных")

def get_data():
    conn = sqlite3.connect('sales.db')
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = get_data()


st.header("1. Текущие показатели продаж")

total_revenue = df['revenue'].sum()
total_qty = df['quantity'].sum()

col1, col2 = st.columns(2)
col1.metric("Общая выручка (руб.)", f"{total_revenue:,.2f}")
col2.metric("Продано товаров (шт.)", total_qty)

st.subheader("Лог продаж из базы данных SQL")
st.dataframe(df, use_container_width=True)

st.subheader("Аналитика выручки по категориям товаров")
category_revenue = df.groupby('category', as_index=False)['revenue'].sum()
st.bar_chart(data=category_revenue, x='category', y='revenue', color='#4AF')

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
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🗑️ Управление базой")

if st.sidebar.button("Очистить все продажи"):
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales")
    conn.commit()
    conn.close()
    st.sidebar.success("Все данные из SQL успешно удалены!")
    st.rerun()


st.header("ИИ-Рекомендации для принятия решений")

if st.button("Сгенерировать бизнес-рекомендации"):
    if df.empty:
        st.warning("База данных SQL пуста. Добавьте продажи, чтобы ИИ мог их проанализировать!")
    else:
        st.info("Агрегация данных SQL и генерация экспертного заключения...")
        
       
        main_category = "Электроника"
        if not category_revenue.empty:
            
            max_row = category_revenue.loc[category_revenue['revenue'].idxmax()]
            main_category = max_row['category']
            
       
        st.success("Рекомендации успешно сформированы ИИ:")
        st.write(f"""
        ### 📊 Экспертное заключение интеллектуальной системы:
        
        1. **Анализ структуры доходов:** На основе развернутых данных СУБД, ключевым драйвером выручки предприятия на текущий момент является категория **"{main_category}"**. Она генерирует наибольший объем денежного потока в цифровом контуре компании.
        
        2. **Управленческое решение по ассортименту:** Рекомендуется оптимизировать складские запасы и увеличить объемы закупок по категории **"{main_category}"** на 15-20% в следующем операционном периоде для предотвращения упущенной прибыли.
        
        3. **Финансовая оптимизация:** Общая накопленная выручка составляет **{total_revenue:,.2f} руб.** С целью максимизации LTV (пожизненной ценности клиентов) рекомендуется запустить таргетированную маркетинговую кампанию в цифровых каналах, сфокусированную на высокомаржинальных позициях.
        """)

