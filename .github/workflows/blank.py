import streamlit as st
import random
import pandas as pd

# Конфигурация датчиков
SENSOR_TYPES = {
    "Термопреобразователь сопротивления": {
        "default_input_min": -196,
        "default_input_max": 600,
        "default_messure1": "°C",
        "default_output_min": 4,
        "default_output_max": 20,
        "default_messure2": "мА",
    },
    "Манометр": {
        "default_input_min": 0.25,
        "default_input_max": 2.5,
        "default_messure1": "МПа",
        "default_output_min": 0,
        "default_output_max": 5,
        "default_messure2": "мА",
    },
    "Электропневматический преобразователь": {
        "default_input_min": 4,
        "default_input_max": 20,
        "default_messure1": "мА",
        "default_output_min": 0.2,
        "default_output_max": 1,
        "default_messure2": "кгс/см2",
    },
    "Термоэлектрический преобразователь": {
        "default_input_min": 313,
        "default_input_max": 1373,
        "default_messure1": "K",
        "default_output_min": 0,
        "default_output_max": 10,
        "default_messure2": "В",
    },
}

# Основной заголовок
st.title("Конфигуратор характеристик прибора")

# Выбор типа датчика
sensor_type = st.selectbox("Выберите тип прибора:", options=list(SENSOR_TYPES.keys()))

if sensor_type:
    sensor_config = SENSOR_TYPES[sensor_type]

    # Поля ввода для параметров
    st.subheader("Входные параметры")
    input_min = st.number_input(
        "Минимальное входное значение:",
        value=sensor_config["default_input_min"],
    )
    input_max = st.number_input(
        "Максимальное входное значение:",
        value=sensor_config["default_input_max"],
    )
    messure1 = st.text_input("Единицы измерения (вход):", value=sensor_config["default_messure1"])

    st.subheader("Выходные параметры")
    output_min = st.number_input(
        "Минимальное выходное значение:",
        value=sensor_config["default_output_min"],
    )
    output_max = st.number_input(
        "Максимальное выходное значение:",
        value=sensor_config["default_output_max"],
    )
    messure2 = st.text_input("Единицы измерения (выход):", value=sensor_config["default_messure2"])

    st.subheader("Дополнительные параметры")
    eror = st.number_input("Приведенная погрешность (%):", min_value=0.01, value=1.0, step=0.01)
    steps = st.number_input("Количество шагов:", min_value=1, value=5, step=1)

    # Кнопка для расчета
    if st.button("Создать конфигурацию"):
        try:
            # Проверка корректности данных
            if input_min >= input_max:
                raise ValueError("Минимальное входное значение должно быть меньше максимального.")
            if output_min >= output_max:
                raise ValueError("Минимальное выходное значение должно быть меньше максимального.")

            # Расчеты
            delta_input = (input_max - input_min) / steps
            delta_output = (output_max - output_min) / steps

            input_values = [input_min + delta_input * i for i in range(steps + 1)]
            ideal_output = [output_min + delta_output * i for i in range(steps + 1)]

            error_values_direct = [random.uniform(-eror, eror) for _ in range(steps + 1)]
            error_values_reverse = [random.uniform(-eror, eror) for _ in range(steps + 1)]

            measured_output_direct = [
                ideal + (ideal * err / 100) for ideal, err in zip(ideal_output, error_values_direct)
            ]
            measured_output_reverse = [
                ideal + (ideal * err / 100) for ideal, err in zip(ideal_output, error_values_reverse)
            ]

            direct_errors = [
                abs((measured - ideal) / (output_max - output_min)) * 100
                for measured, ideal in zip(measured_output_direct, ideal_output)
            ]
            reverse_errors = [
                abs((measured - ideal) / (output_max - output_min)) * 100
                for measured, ideal in zip(measured_output_reverse, ideal_output)
            ]

            # Создание таблицы результатов
            data = {
                f"Идеальное входное значение ({messure1})": input_values,
                f"Идеальное выходное значение ({messure2})": ideal_output,
                f"Измеренное значение (прямой ход, {messure2})": measured_output_direct,
                f"Измеренное значение (обратный ход, {messure2})": measured_output_reverse,
                "Погрешность (прямой ход, %)": direct_errors,
                "Погрешность (обратный ход, %)": reverse_errors,
            }

            results_df = pd.DataFrame(data)

            # Проверка соответствия точности
            is_valid = all(err <= eror for err in direct_errors + reverse_errors)

            # Отображение результатов
            st.subheader("Результаты:")
            st.dataframe(results_df)

            if is_valid:
                st.success("Прибор соответствует заданной точности.")
            else:
                st.error("Прибор не соответствует заданной точности.")

            # Сохранение результатов в CSV
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Скачать результаты в CSV",
                data=csv,
                file_name="sensor_results.csv",
                mime="text/csv",
            )
        except ValueError as e:
            st.error(f"Ошибка: {e}")
