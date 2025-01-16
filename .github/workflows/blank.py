import streamlit as st
import numpy as np
import pandas as pd
import random

# Конфигурация типов датчиков
SENSOR_TYPES = {
    "Термопреобразователь сопротивления": {
        "default_input_min": -196,
        "default_input_max": 600,
        "default_messure1": "°C",
        "default_output_min": 4,
        "default_output_max": 20,
        "default_messure2": "мА"
    },
    "Манометр": {
        "default_input_min": 0.25,
        "default_input_max": 2.5,
        "default_messure1": "МПа",
        "default_output_min": 0,
        "default_output_max": 5,
        "default_messure2": "мА"
    },
    "Датчик уровня": {
        "default_input_min": 0,
        "default_input_max": 100,
        "default_messure1": "м",
        "default_output_min": 0,
        "default_output_max": 20,
        "default_messure2": "мА"
    },
    "Термоэлектрический преобразователь": {
        "default_input_min": 313,
        "default_input_max": 1373,
        "default_messure1": "K",
        "default_output_min": 0,
        "default_output_max": 10,
        "default_messure2": "В"
    }
}

def generate_sensor_data(input_min, input_max, output_min, output_max, error_limit):
    """Генерация данных для датчика"""
    # Создание 6 точек измерения
    input_points = np.linspace(input_min, input_max, 6)
    output_points = np.linspace(output_min, output_max, 6)

    # Генерация случайных погрешностей
    random_errors = np.random.uniform(-1, 1, 12)

    # Расчет данных
    data = []
    is_suitable = True

    for i in range(6):
        # Прямой и обратный ход с погрешностями
        forward_output = output_points[i] + (random_errors[i] / 100)
        backward_output = output_points[i] + (random_errors[i+6] / 100)

        # Расчет погрешностей
        forward_error = 100 * abs(forward_output - output_points[i]) / (output_max - output_min)
        backward_error = 100 * abs(backward_output - output_points[i]) / (output_max - output_min)

        # Проверка соответствия погрешности
        if forward_error > error_limit or backward_error > error_limit:
            is_suitable = False

        # Формирование строки данных
        row = {
            "Входное значение": f"{input_points[i]:.3f}",
            "Выходное значение": f"{output_points[i]:.3f}",
            "Прямой ход": f"{forward_output:.3f}",
            "Обратный ход": f"{backward_output:.3f}",
            "Погрешность прямого хода": f"{forward_error:.3f}",
            "Погрешность обратного хода": f"{backward_error:.3f}"
        }
        data.append(row)

    return pd.DataFrame(data), is_suitable

def main():
    st.title("Поверка и Калибровка Датчиков")

    # Sidebar для выбора типа датчика
    st.sidebar.header("Параметры датчика")
    sensor_type = st.sidebar.selectbox(
        "Выберите тип датчика",
        list(SENSOR_TYPES.keys())
    )

    # Получение default значений
    sensor_config = SENSOR_TYPES[sensor_type]

    # Колонки для ввода параметров
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Входные параметры")
        input_min = st.number_input(
            f"Минимальное входное значение ({sensor_config['default_messure1']})", 
            value=sensor_config['default_input_min'],
            step=0.1
        )
        input_max = st.number_input(
            f"Максимальное входное значение ({sensor_config['default_messure1']})", 
            value=sensor_config['default_input_max'],
            step=0.1
        )

    with col2:
        st.subheader("Выходные параметры")
        output_min = st.number_input(
            f"Минимальное выходное значение ({sensor_config['default_messure2']})", 
            value=sensor_config['default_output_min'],
            step=0.1
        )
        output_max = st.number_input(
            f"Максимальное выходное значение ({sensor_config['default_messure2']})", 
            value=sensor_config['default_output_max'],
            step=0.1
        )

    # Погрешность
    error_limit = st.sidebar.number_input(
        "Предельная погрешность (%)", 
        min_value=0.0, 
        max_value=10.0, 
        value=1.0, 
        step=0.1
    )

    # Кнопка генерации
    if st.button("Выполнить поверку"):
        # Проверки корректности
        if input_min >= input_max:
            st.error("Минимальное входное значение должно быть меньше максимального")
            return

        if output_min >= output_max:
            st.error("Минимальное выходное значение должно быть меньше максимального")
            return

        # Генерация данных
        df, is_suitable = generate_sensor_data(
            input_min, input_max, 
            output_min, output_max, 
            error_limit
        )

        # Отображение результатов
        st.header("Результаты поверки")
        
        # Статус пригодности
        if is_suitable:
            st.success("Прибор ПРИГОДЕН к эксплуатации")
            status_color = "green"
        else:
            st.error("Прибор НЕ ПРИГОДЕН к эксплуатации")
            status_color = "red"

        # Таблица результатов
        st.dataframe(df)

        # Графическое представление погрешностей
        st.header("Графический анализ")
        
        # Создание графика погрешностей
        chart_data = pd.DataFrame({
            'Погрешность прямого хода': df['Погрешность прямого хода'].astype(float),
            'Погрешность обратного хода': df['Погрешность обратного хода'].astype(float)
        }, index=df['Входное значение'])
        
        st.line_chart(chart_data)

        # Кнопка экспорта
        csv = df.to_csv(index=False, sep=';')
        st.download_button(
            label="Скачать отчет (CSV)",
            data=csv,
            file_name=f'{sensor_type}_calibration_report.csv',
            mime='text/csv'
        )

    # Справка
    st.sidebar.header("Справка")
    with st.sidebar.expander("Инструк ции"):
        st.write("""
        1. **Выбор типа датчика**: Выберите тип датчика из выпадающего списка.
        2. **Входные параметры**: Укажите минимальное и максимальное входные значения.
        3. **Выходные параметры**: Укажите минимальное и максимальное выходные значения.
        4. **Погрешность**: Задайте предельную погрешность в процентах.
        5. **Выполнить поверку**: Нажмите кнопку для генерации результатов.
        6. **Результаты**: Просмотрите результаты поверки и графический анализ.
        7. **Экспорт**: Скачайте отчет в формате CSV.
        """)

if __name__ == "__main__":
    main()
