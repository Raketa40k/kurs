import streamlit as st
import pandas as pd
import numpy as np
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

def generate_sensor_data(input_min, input_max, output_min, output_max, eror):
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
        if forward_error > eror or backward_error > eror:
            is_suitable = False

        # Формирование строки данных
        row = [
            f"{input_points[i]:.3f}",
            f"{output_points[i]:.3f}",
            f"{forward_output:.3f}",
            f"{backward_output:.3f}",
            f"{forward_error:.3f}",
            f"{backward_error:.3f}"
        ]
        data.append(row)

    return data, is_suitable

def main():
    st.title("Конфигуратор и Поверка Датчиков")

    # Sidebar для выбора типа датчика
    st.sidebar.header("Параметры датчика")
    sensor_type = st.sidebar.selectbox(
        "Выберите тип датчика",
        list(SENSOR_TYPES.keys())
    )

    # Получение default значений
    sensor_config = SENSOR_TYPES[sensor_type]

    # Входные параметры
    col1, col2 = st.columns(2)
    with col1:
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

    # Выходные параметры
    with col2:
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
    eror = st.sidebar.number_input(
        "Предельная погрешность (%)", 
        min_value=0.0, 
        max_value=10.0, 
        value=1.0, 
        step=0.1
    )

    # Кнопка генерации
    if st.button("Сгенерировать результаты"):
        # Проверки корректности
        if input_min >= input_max:
            st.error("Минимальное входное значение должно быть меньше максимального")
            return

        if output_min >= output_max:
            st.error("Минимальное выходное значение должно быть меньше максимального")
            return

        # Генерация данных
        data, is_suitable = generate_sensor_data(
            input_min, input_max, 
            output_min, output_max, 
            eror
        )

        # Создание DataFrame
        df = pd.DataFrame(
            data, 
            columns=[
                f"Входное значение ({sensor_config['default_messure1']})", 
                f"Выходное значение ({sensor_config['default_messure2']})",
                "Прямой ход", 
                "Обратный ход",
                "Погрешность прямого хода",
                "Погрешность обратного хода"
            ]
        )

        # Отображение результатов
        st.header("Результаты поверки")
        
        # Статус пригодности
        if is_suitable:
            st.success("Прибор пригоден к эксплуатации")
        else:
            st.error("Прибор не пригоден к эксплуатации")

        # Таблица результатов
        st.dataframe(df)

        # Кнопка экспорта
        csv = df.to_csv(index=False, sep=';')
        st.download_button(
            label="Скачать результаты (CSV)",
            data=csv,
            file_name=f'{sensor_type}_results.csv',
            mime='text/csv'
        )

        # Графическое представление
        st.header("Графическое представление")
        
        # График погрешностей
        chart_data = pd.DataFrame({
            'Прямой ход': df['Погрешность прямого хода'].astype(float),
            'Обратный ход': df['Погрешность обратного хода'].astype(float)
        }, index=df[f"Входное значение ({sensor_config['default_messure1']})"])
        
        st.line_chart(chart_data)

if __name__ == "__main__":
    main()
