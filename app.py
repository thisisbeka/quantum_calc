import streamlit as st
from mpmath import mp
from fpdf import FPDF
import tempfile
import os

# Функция вычисления промежуточного результата по новым границам
def calculate_peremnozhator_new(x_val_str, y_val_str, n_val_str):
    try:
        x_val = mp.mpf(x_val_str)
        y_val = mp.mpf(y_val_str)
        n_val = int(n_val_str)
    except ValueError:
        return None, "Неверный ввод. Пожалуйста, введите числа для x, y и целое число для n."

    if n_val <= 0:
        return None, "Неверный ввод. n должно быть положительным целым числом."

    # Разрядности
    Rx = len(x_val_str.replace('.', '').replace('-', ''))
    Ry = len(y_val_str.replace('.', '').replace('-', ''))

    try:
        # Вычисляем степень и устанавливаем точность
        power = -(mp.mpf(Rx) * mp.mpf(Ry) * (mp.mpf(n_val) ** 2))
        required_precision = int(abs(power) * mp.log10(10)) + 1000
        if required_precision < 100:
            required_precision = 100
        mp.dps = required_precision

        # Основное вычисление
        denominator = (mp.mpf(1) - y_val * mp.power(10, power))
        if denominator == 0:
            return None, "Ошибка: Деление на ноль. Измените входные значения."

        calculation = x_val / denominator
        full_str = mp.nstr(calculation, n=mp.dps)

        # Выделяем дробную часть
        if '.' in full_str:
            _, dec_part = full_str.split('.')
        else:
            dec_part = ''

        # Границы
        interval = Rx * Ry * (n_val ** 2)
        upper = interval * n_val
        lower = upper - interval

        # Дополняем нулями при необходимости
        if len(dec_part) < upper:
            dec_part = dec_part.ljust(upper, '0')

        # Берем цифры с (lower+1)-й по upper-ю после точки
        intermediate = dec_part[lower:upper]
        return intermediate, Rx, Ry

    except Exception as e:
        return None, f"Ошибка вычисления: {str(e)}"

# Функция экспорта в PDF с промежуточным результатом
def export_to_pdf_new(x, y, n, Rx, Ry, intermediate):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", "", 12)
    except RuntimeError:
        st.warning(
            "Font 'DejaVuSans.ttf' not found. Please ensure it's in the same directory as the script for proper PDF generation.")
        pdf.set_font("Arial", "", 12)

    formula = f"{x} / (1 - {y} * 10^(-({Rx} * {Ry} * {n}^2)))"
    pdf.text(10, 10, "Формула: " + formula)
    pdf.text(10, 20, f"Rx (разрядность x): {Rx}")
    pdf.text(10, 30, f"Ry (разрядность y): {Ry}")
    pdf.text(10, 40, f"Промежуточный результат: {intermediate}")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Интерфейс Streamlit
st.title("Перемножатор Калькулятор")

x_input = st.text_input("Первое число (x)", "25")
y_input = st.text_input("Второе число (y)", "32")
n_input = st.text_input("Количество умножений (n)", "1")

if st.button("Вычислить"):
    result = calculate_peremnozhator_new(x_input, y_input, n_input)
    intermediate, *rest = result
    if intermediate:
        Rx_val, Ry_val = rest
        st.text(f"Rx (разрядность x): {Rx_val}")
        st.text(f"Ry (разрядность y): {Ry_val}")
        st.text(f"Результат: {intermediate}")

        pdf_path = export_to_pdf_new(x_input, y_input, n_input, Rx_val, Ry_val, intermediate)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Скачать PDF",
                data=pdf_file,
                file_name="peremnozhator_calculation_new.pdf",
                mime="application/pdf"
            )
        os.unlink(pdf_path)
    else:
        error_msg = rest[0] if rest else 'Неизвестная ошибка'
        st.error(error_msg)
