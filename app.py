from math import sqrt
from sys import argv

from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QTextBrowser
from PyQt5.QtGui import QFontDatabase

import design

# pushButton - кнопка «Рассчитать»
# a_field - поле для ввода a
# b_field - поле для ввода b
# h_field - поле для ввода h
# answer_text - поле для вывода ответа 

class ExampleApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        """Метод инициализации интерфейса."""
        super().__init__()
        QFontDatabase.addApplicationFont('fonts/circe.ttf')
        QFontDatabase.addApplicationFont('fonts/circe-bold.ttf')
        QFontDatabase.addApplicationFont('fonts/circe-extrabold.ttf')
        self.setupUi(self)
        self.pushButton.clicked.connect(self.count_1)
        self.pushButton_2.clicked.connect(self.count_2)

    def __text_to_html(self, text, font_family='Circe', font_size=14):
        """Возвращает HTML-разметку для поля вывода ответа с переданным текстом text."""
        print(font_size)
        return f'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html>
<head>
    <meta name="qrichtext" content="1" />
    <style type="text/css">
        p, li {{ white-space: pre-wrap; }}
    </style>
</head>
<body style=" font-family:'{font_family}'; font-size:{font_size}pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
<span style=" font-family:'{font_family}'; font-size:{font_size}pt;">{text}</span></p>
</body>
</html>'''

    def __get_numbers_from_fields(self, tab_number: int):
        """Возвращает кортеж значений, введённых на вкладке tab_number.
        Если в полях введён текст, возвращает None."""
        if tab_number == 1:
            try:
                fields = (self.a_field.text(), self.b_field.text(), self.h_field.text())
                a, b, h = tuple(map(int, fields))
            except ValueError:
                if fields == ('', '', ''):
                    fields = (self.a_field.placeholderText(), self.b_field.placeholderText(), self.h_field.placeholderText())
                    a, b, h = tuple(map(int, fields))
                    self.a_field.setText(str(a))
                    self.b_field.setText(str(b))
                    self.h_field.setText(str(h))
                else:
                    return None
            
            return (a, b, h)
        elif tab_number == 2:
            try:
                fields = (self.a_field_2.text(), self.b_field_2.text(), self.h_field_2.text())
                a, b, h = tuple(map(int, fields))
            except ValueError:
                if fields == ('', '', ''):
                    fields = (self.a_field_2.placeholderText(), self.b_field_2.placeholderText(), self.h_field_2.placeholderText())
                    a, b, h = tuple(map(int, fields))
                    self.a_field_2.setText(str(a))
                    self.b_field_2.setText(str(b))
                    self.h_field_2.setText(str(h))
                else:
                    return None
            
            return (a, b, h)

    def set_answer(self, answer, tab_number: int, font_family='Circe', font_size=14):
        """Устанавливает ответ answer в поле ответа."""
        if tab_number == 1:
            return self.answer_text.setHtml(self.__text_to_html(answer, font_family, font_size))
        elif tab_number == 2:
            return self.answer_text_2.setHtml(self.__text_to_html(answer, font_family, font_size))

    def count_1(self):
        """Выполняет расчёты во вкладке 1 на основании данных значений."""
        Rs = 270        # МПа  - растянутая арматура класса A300
        αr = 0.41       # Значение для арматуры класса А300 (с. 21, таблица 3.2)
        ξR = 0.577      # Значение для арматуры А300 (с. 21, таблица 3.2)
        Rb = 8.5        # МПа  - бетон класса B15
        M = 200 * 10**6 # кН·м - изгибающий момент с учетом кратковр. нагрузок

        # Валидация введённых значений
        fields = self.__get_numbers_from_fields(1)

        if fields == None:
            # Если в строках введён текст, а не числа, пишем об этом в поле ответа
            return self.set_answer('Введены не числа. Повторите попытку.', 1)
        else:
            # Если введены числа, продолжает расчёты
            a, b, h = fields

        h0 = h - a # мм

        try:
            αm = M / (Rb * b * h0 * h0)
            if αm <= αr:
                As = round((Rb * b * h0 * (1 - sqrt(1 - 2 * αm))) / Rs, 3)
                self.set_answer(f'{As} мм²', 1)
            else:
                noticement_text = 'При введённых данных αm > αr. Требуется увеличить сечение либо установить сжатую арматуру. Нажмите на кнопку повторно для расчёта сжатой арматуры.'
                current_text = self.answer_text.toPlainText()
                if current_text == noticement_text:
                    As_ = (M - αr * Rb * b * h0 * h0) / (Rs * (h0 - a))
                    As = round((ξR * Rb * b * h0) / Rs + As_, 3)

                    if As > 0:
                        self.set_answer(f'Значение для сжатой арматуры: {As} мм²', 1)
                    else:
                        self.set_answer(
                            f'Получено отрицательное значение ({As} мм²). '
                            'Следует принять площадь сечения арматуры с учетом конструктивных требований '
                            'и минимального % армирования в зависимости от гибкости элемента.',
                            tab_number=1,
                            font_size=12
                        )
    
                else:
                    self.set_answer(noticement_text, 1, font_size=12)

        except ZeroDivisionError:
            # Обработчик ошибки деления на ноль
            self.set_answer(f'Обнаружено деление на ноль. Измените входные данные.')
            return

    def count_2(self):
        """Выполняет расчёты во вкладке 2 на основании данных значений."""
        Rs = 355    # МПа  - растянутая арматура класса A400
        As = 2945   # мм²  - площадь сечения арматуры (6Ø25)
        Rb = 14.5   # МПа  - бетон класса B25
        M = 550     # кН·м - изгибающий момент 
        ξR = 0.531  # Значение для арматуры А400 (с. 21, таблица 3.2)

        # Валидация введённых значений
        fields = self.__get_numbers_from_fields(2)

        if fields == None:
            # Если в строках введён текст, а не числа, пишем об этом в поле ответа
            return self.set_answer('Введены не числа. Повторите попытку.', 2)
        else:
            # Если введены числа, продолжает расчёты
            a, b, h = fields

        h0 = h - a # мм

        try:
            x = (Rs * As) / (Rb * b) # мм
            ξ = x / h0
            if ξ < ξR:
                # Условие 3.20
                case = round((Rs * As * (h0 - 0.5 * x)) / 10**6, 1)
                if M <= case:
                    return self.set_answer(f'M = {M} кН·м ⩽ {case} кН·м, прочность сечения обеспечена.', 2)
                else:
                    return self.set_answer(f'M = {M} кН·м > {case} кН·м, прочность сечения НЕ обеспечена.', 2)
            else:
                # Условие 3.21
                αr = ξR * (1 - 0.5 * ξR)
                case = round((αr * Rb * h0 * h0), 1)
                if M <= case:
                    return self.set_answer(f'M = {M} кН·м ⩽ {case} кН·м, прочность сечения обеспечена.', 2)
                else:
                    return self.set_answer(f'M = {M} кН·м > {case} кН·м, прочность сечения НЕ обеспечена.', 2)
        except ZeroDivisionError:
            # Обработчик ошибки деления на ноль
            self.set_answer(f'Обнаружено деление на ноль. Измените входные данные.', 2)
            return


def main():
    app = QApplication(argv) 
    window = ExampleApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()