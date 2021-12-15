from dataclasses import dataclass, field
from math import sqrt
from sys import argv

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QPixmap
from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QGraphicsPixmapItem, QGraphicsScene

from ui import mainwindow, table, info
from resources import resource_path, concrete, armature, sortament, Values



# Переменная для хранения предыдущих значений в задаче 2
previous_fields: Values = None


def armature_output(value):
    value /= 100 # мм² → см²
    found = tuple(sortament.keys())[0] # найденное значение (первоначально первое)
    for arm in tuple(sortament):
        if abs(arm - value) < abs(found - value):
            found = arm
    
    return sortament[found]


class ExampleApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        """Метод инициализации интерфейса."""
        super().__init__()
        QFontDatabase.addApplicationFont(resource_path('fonts/circe.ttf'))
        QFontDatabase.addApplicationFont(resource_path('fonts/circe-bold.ttf'))
        QFontDatabase.addApplicationFont(resource_path('fonts/circe-extrabold.ttf'))
        self.setupUi(self)
        # Привязка клавиш к функциям
        self.pushButton.clicked.connect(self.count)
        # self.pushButton_2.clicked.connect(self.count_2)
        self.btn_showTable.clicked.connect(self.show_table)
        self.infoButton.clicked.connect(self.show_info)
        
        ###
        self.table_window = table.Ui_Dialog()
        self.info_window = info.Ui_Dialog()
        
        pixmap = QPixmap()
        pixmap.load(resource_path('img/picture.png'))
        item_picture = QGraphicsPixmapItem(pixmap)
        # item_picture.setScale(1)
        self.scene_picture = QGraphicsScene(self)
        self.scene_picture.addItem(item_picture)
        # self.graphicsView_2.fitInView(self.scene_picture.itemsBoundingRect())
        self.graphicsView_2.setScene(self.scene_picture)
        
        
    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        self.graphicsView_2.fitInView(self.scene_picture.itemsBoundingRect(), Qt.KeepAspectRatio)
        return super().resizeEvent(e)
    
    
    def show_table(self):
        self.table_window.show()
        self.table_window.table_zoom.fitInView(self.table_window.scene_table.itemsBoundingRect(), Qt.KeepAspectRatio)
        
        
    def show_info(self):
        self.info_window.show()


    def __text_to_html(self, text, font_family='Circe', font_size=14):
        """Возвращает HTML-разметку для поля вывода ответа с переданным текстом text."""
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


    def count(self):
        if self.tabWidget.currentIndex() == 0:
            self.count_1()
        elif self.tabWidget.currentIndex() == 1:
            self.count_2()
    
    
    @staticmethod
    def __get_float_field(field: QLineEdit):
        try:
            return float(field.text())
        except ValueError:
            if field.text() == '':
                field.setText(field.placeholderText())
                return float(field.placeholderText())
            else:
                return None


    def __get_numbers_from_fields(self) -> Values:
        """Возвращает датакласс значений, введённых на вкладке tab_number.
        Если в полях введён текст, возвращает None."""
        
        if self.tabWidget.currentIndex() == 0:
            concrete_type = self.concrete_type.currentText()
            armature_type = self.armature_type.currentText()
            fields = (
                self.a_field, 
                self.b_field, 
                self.h_field,
                self.M_field
            )
        elif self.tabWidget.currentIndex() == 1:
            concrete_type = self.concrete_type_2.currentText()
            armature_type = self.armature_type_2.currentText()
            fields = (
                self.a_field_2, 
                self.b_field_2, 
                self.h_field_2,
                self.M_field_2,
                self.As_field
            )
            
        values = tuple((self.__get_float_field(field) for field in fields))
        
        if None in values:
            return None
        
        if len(values) == 4:
            return Values(*values, concrete_type, armature_type)
        else:
            return Values(*values[:-1], concrete_type, armature_type, values[-1])


    def set_answer(self, answer, font_family='Circe', font_size=14):
        """Устанавливает ответ answer в поле ответа."""
        if self.tabWidget.currentIndex() == 0:
            return self.answer_text.setHtml(self.__text_to_html(answer, font_family, font_size))
        elif self.tabWidget.currentIndex() == 1:
            return self.answer_text_2.setHtml(self.__text_to_html(answer, font_family, font_size))


    def count_1(self):
        """Выполняет расчёты во вкладке 1 на основании данных значений."""
        
        # Получение и валидация введённых значений
        fields = self.__get_numbers_from_fields()
        
        if fields == None:
            # Если в строках введён текст, а не числа, пишем об этом в поле ответа
            return self.set_answer('Введены не числа. Повторите попытку.')
        else:
            fields.M *= 10**6
            # Если введены числа, продолжаем расчёты
            a, b, h, M = fields.a, fields.b, fields.h, fields.M
            if a > h:
                return self.set_answer('Значение a не может быть больше h. Повторите попытку.')
        
        current_armature = armature[fields.armature_type]
        
        Rs = current_armature['Rs']         # МПа  - растянутая арматура класса A300
        αr = current_armature['a_r']        # Значение для арматуры класса А300 (с. 21, таблица 3.2)
        ξR = current_armature['xi_r']       # Значение для арматуры А300 (с. 21, таблица 3.2)
        Rb = concrete[fields.concrete_type] # МПа  - бетон класса B15

        global previous_fields

        

        h0 = h - a # мм

        try:
            # Формула 3.22 для вычисления значения αm
            αm = M / (Rb * b * h0 * h0)
            if αm <= αr:
                # Формула 3.23 для вычисления площади сечения растянутой арматуры
                As = round((Rb * b * h0 * (1 - sqrt(1 - 2 * αm))) / Rs, 3)
                self.set_answer(f'{As} мм² ({armature_output(As)})')
                self.As_field.setText(str(As))
            else:
                # Условие гласит, что при αm > αr требуется увеличить сечение,
                # или повысить класс бетона, или установить сжатую арматуру согласно
                # п. 3.22

                noticement_text = 'При введённых данных αm > αr. Требуется увеличить сечение, повысить класс бетона либо установить сжатую арматуру. Нажмите на кнопку повторно для расчёта сжатой арматуры.'
                current_text = self.answer_text.toPlainText()
    
                if current_text == noticement_text and fields == previous_fields:
                    # Если текст о несоответствии условию уже находится в поле ответа, 
                    # а значения остались теми же, значит, пользователь требует
                    # расчёта сжатой арматуры согласно п. 3.22
                    As_ = (M - αr * Rb * b * h0 * h0) / (Rs * (h0 - a))
                    As = round((ξR * Rb * b * h0) / Rs + As_, 3)

                    if As > 0:
                        self.set_answer(f'Значение для сжатой арматуры: {As} мм² ({armature_output(As)})')
                        self.As_field.setText(str(As))
                    else:
                        self.set_answer(
                            f'Получено отрицательное значение ({As} мм²). '
                            'Следует принять площадь сечения арматуры с учетом конструктивных требований '
                            'и минимального % армирования в зависимости от гибкости элемента.',
                            font_size=12
                        )
    
                else:
                    # Выводим соответствующее сообщение о несоответствии условию
                    self.set_answer(noticement_text, font_size=12)
            
            # Для хранения предыдущих значений записываем их в кортеж previous_values
            previous_fields = Values(a, b, h, M, fields.concrete_type, fields.armature_type)

        except ZeroDivisionError:
            # Обработчик ошибки деления на ноль
            return self.set_answer(f'Обнаружено деление на ноль. Измените входные данные.')


    def count_2(self):
        """Выполняет расчёты во вкладке 2 на основании данных значений."""
        # Получение и валидация введённых значений
        fields = self.__get_numbers_from_fields()
        
        if fields == None:
            # Если в строках введён текст, а не числа, пишем об этом в поле ответа
            return self.set_answer('Введены не числа. Повторите попытку.')
        else:
            # Если введены числа, продолжаем расчёты
            a, b, h, M, As = fields.a, fields.b, fields.h, fields.M, fields.As
            if a > h:
                return self.set_answer('Значение a не может быть больше h. Повторите попытку.')
        
        current_armature = armature[fields.armature_type]
        
        Rs = current_armature['Rs']    # МПа  - растянутая арматура класса A400
        Rb = concrete[fields.concrete_type]   # МПа  - бетон класса B25
        ξR = current_armature['xi_r']  # Значение для арматуры А400 (с. 21, таблица 3.2)

        h0 = h - a # мм

        try:
            x = (Rs * As) / (Rb * b) # мм
            ξ = x / h0
            if ξ < ξR:
                # Условие 3.20
                case = round((Rs * As * (h0 - 0.5 * x)) / 10**6, 1)
                if M <= case:
                    return self.set_answer(f'M = {M} кН·м ⩽ {case} кН·м, прочность сечения обеспечена.')
                else:
                    return self.set_answer(f'M = {M} кН·м > {case} кН·м, прочность сечения НЕ обеспечена.')
            else:
                # Условие 3.21
                αr = ξR * (1 - 0.5 * ξR)
                case = round((αr * Rb * h0 * h0), 1)
                if M <= case:
                    return self.set_answer(f'M = {M} кН·м ⩽ {case} кН·м, прочность сечения обеспечена.')
                else:
                    return self.set_answer(f'M = {M} кН·м > {case} кН·м, прочность сечения НЕ обеспечена.')
        except ZeroDivisionError:
            # Обработчик ошибки деления на ноль
            self.set_answer(f'Обнаружено деление на ноль. Измените входные данные.')
            return


def main():
    app = QApplication(argv)
    
    #open qss file
    with open(resource_path("ui/Combinear.qss"), "r") as file:
        qss = file.read()
        app.setStyleSheet(qss)
        
    window = ExampleApp()
    window.show()
    window.graphicsView_2.fitInView(window.scene_picture.itemsBoundingRect(), Qt.KeepAspectRatio)
    app.exec_()


if __name__ == '__main__':
    main()