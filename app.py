import streamlit as st
from mpmath import mp
from fpdf import FPDF
import tempfile

# Функция для расчета квантовой формулы с использованием mpmath
def calculate_quantum(base, exponent):
    try:
        m = int(base)
        n = int(exponent)
    except ValueError:
        return None, "Неверный ввод. Пожалуйста, введите положительные целые числа."

    if m <= 0 or n < 0:
        return None, "Неверный ввод. Пожалуйста, введите положительные целые числа."

    m_digits = len(str(m))
    power = -n * m_digits

    try:
        # Устанавливаем точность вычислений для получения только последней строки
        required_precision = n * m_digits * n + 1  # Увеличиваем точность на 1, чтобы учесть первую единицу
        mp.dps = required_precision  # Устанавливаем количество значащих цифр

        calculation = mp.mpf(1) / (mp.mpf(1) - mp.mpf(m) * mp.power(10, power))
        result_string = mp.nstr(calculation, n=required_precision).rstrip('0')
        digit_count = len(result_string.replace('.', ''))  # Учитываем только цифры

        # Получаем последнюю строку
        formatted_result = result_string.replace(".", "")[1:]  # Удаляем первую единицу
        line_length = n * m_digits
        total_length = n * line_length
        last_line = formatted_result[-total_length:][-line_length:]

        return result_string, digit_count, last_line
    except Exception as e:
        return None, f"Ошибка вычисления: {str(e)}", None

# Функция для экспорта результата в PDF
def export_to_pdf(base, exponent, digit_count, last_line):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    formula = f"{base}^{exponent} = 1/(1-{base}*10^(-{exponent}*{len(base)}))"
    pdf.text(10, 10, formula)
    pdf.text(10, 20, f"Результат содержит {digit_count} знаков")
    pdf.text(10, 30, f"Ответ: {last_line}")

    # Сохраняем PDF во временный файл
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Интерфейс Streamlit
st.title("Квантовый калькулятор")

base = st.text_input("Основание (m)", "497")
exponent = st.text_input("Степень (n)", "12")

if st.button("Вычислить"):
    result, digit_count_or_error, last_line = calculate_quantum(base, exponent)
    if result:
        st.success(f"Результат содержит {digit_count_or_error - 1} знаков")  # Учитываем удаление первой единицы
        st.text(f"Ответ: {last_line}")

        # Создаем PDF и сохраняем путь к файлу
        pdf_path = export_to_pdf(base, exponent, digit_count_or_error - 1, last_line)

        # Предоставляем кнопку для скачивания PDF
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Скачать PDF",
                data=pdf_file,
                file_name="quantum_calculation.pdf",
                mime="application/pdf"
            )
    else:
        st.error(digit_count_or_error)
