import streamlit as st
from mpmath import mp
from fpdf import FPDF
import tempfile
import os


# Function to calculate the new formula: x / (1 - y * 10^(-(Rx * Ry * n^2)))
def calculate_peremnozhator_new(x_val_str, y_val_str, n_val_str):
    try:
        x_val = mp.mpf(x_val_str)
        y_val = mp.mpf(y_val_str)
        n_val = int(n_val_str)
    except ValueError:
        return None, "Неверный ввод. Пожалуйста, введите числа для x, y и целое число для n."

    if n_val <= 0:
        return None, "Неверный ввод. n должно быть положительным целым числом."

    # Calculate Rx (number of digits in x) and Ry (number of digits in y)
    # For floating point numbers, we consider digits before and after decimal
    Rx = len(x_val_str.replace('.', '').replace('-', ''))
    Ry = len(y_val_str.replace('.', '').replace('-', ''))

    try:
        # Calculate the exponent part: -(Rx * Ry * n^2)
        power = -(mp.mpf(Rx) * mp.mpf(Ry) * (mp.mpf(n_val) ** 2))

        # Determine required precision. This is a heuristic.
        # A more robust precision calculation might be needed for extreme values.
        required_precision = int(abs(power) * mp.log10(10)) + 50  # Base 10 log of 10 is 1
        if required_precision < 100:
            required_precision = 100
        mp.dps = required_precision

        denominator = (mp.mpf(1) - y_val * mp.power(10, power))
        if denominator == 0:
            return None, "Ошибка: Деление на ноль. Измените входные значения."

        calculation = x_val / denominator

        result_string = mp.nstr(calculation, n=required_precision)

        digit_count = len(result_string.replace(".", "").replace("-", ""))

        return result_string, digit_count, Rx, Ry
    except Exception as e:
        return None, f"Ошибка вычисления: {str(e)}", None, None


# Function to export result to PDF
def export_to_pdf_new(x, y, n, Rx, Ry, result_string, digit_count):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", "", 12)
    except RuntimeError:
        st.warning(
            "Font \'DejaVuSans.ttf\' not found. Please ensure it\'s in the same directory as the script for proper PDF generation.")
        pdf.set_font("Arial", "", 12)

    formula = f"{x} / (1 - {y} * 10^(-({Rx} * {Ry} * {n}^2)))"
    pdf.text(10, 10, "Формула: " + formula)
    pdf.text(10, 20, f"Rx (разрядность x): {Rx}")
    pdf.text(10, 30, f"Ry (разрядность y): {Ry}")
    pdf.text(10, 40, f"Результат содержит {digit_count} знаков")
    pdf.text(10, 50, f"Ответ: {result_string}")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name


# Streamlit Interface
st.title("Перемножатор Калькулятор")

x_input = st.text_input("Первое число (x)", "25")
y_input = st.text_input("Второе число (y)", "32")
n_input = st.text_input("Количество умножений (n)", "1")

if st.button("Вычислить"):
    result, digit_count_or_error, Rx_val, Ry_val = calculate_peremnozhator_new(x_input, y_input, n_input)
    if result:
        st.success(f"Результат содержит {digit_count_or_error} знаков")
        st.text(f"Ответ: {result}")
        st.text(f"Rx (разрядность x): {Rx_val}")
        st.text(f"Ry (разрядность y): {Ry_val}")

        pdf_path = export_to_pdf_new(x_input, y_input, n_input, Rx_val, Ry_val, result, digit_count_or_error)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Скачать PDF",
                data=pdf_file,
                file_name="peremnozhator_calculation_new.pdf",
                mime="application/pdf"
            )
        os.unlink(pdf_path)
    else:
        st.error(digit_count_or_error)


