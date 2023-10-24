import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import QtCore, QtGui
import xlwings as xw
import qdarkstyle
from search import Ui_Form
import torch
import cv2
from torchvision import transforms
from Model import myNet

class MainWindow(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__() # 继承search.py Ui_Form
        self.setupUi(self)

        # click button 事件连结
        self.open_image.clicked.connect(self.openImage)
        self.confirm_upload_button.clicked.connect(self.uploadInfo)

        # 保存+载入模型
        self.model = myNet()
        torch.save(self.model, "diagnose.py")
        self.model = torch.load("diagnose.py")
        self.model.eval()

        # 自动实时执行search,无button
        self.find_id.returnPressed.connect(self.search)

    def openImage(self):  # 选择本地图片上传
        global imgName
        imgName, imgType = QFileDialog.getOpenFileName(self.tabWidget_2, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        # 弹出一个文件选择框，第一个返回值imgName记录选中的文件路径+文件名，第二个返回值imgType记录文件的类型
        jpg = QtGui.QPixmap(imgName)#.scaled(self.image_input.width(), self.image_input.height())  # 通过文件路径获取图片文件，并设置图片长宽为label控件的长款
        self.image_input.setPixmap(jpg)
        self.image_path.setText(imgName)

        # 保存图片到本地
        global fd
        fd = f"C:/Engineering/dataset/filestorage/{self.enter_name.text()}.png"
        jpg.save(fd)

    def uploadInfo(self):
        input_id = self.enter_id.text()
        input_name = self.enter_name.text()
        input_gender = self.enter_gender.text()
        input_age = self.enter_age.text()
        input_height = self.enter_height.text()
        input_weight = self.enter_weight.text()

        # 对图片进行图像预处理
        picture = cv2.imread(f'{self.image_path.text()}')
        array = cv2.resize(picture, (64, 64))  # cv2 格式
        transform = transforms.ToTensor()  # 用transform to tensor 将cv2的gbr通道改为rgb通道
        data = transform(array).unsqueeze(0)
        # 对数据进行诊断
        y = self.model(data)
        if y >= 0.5:
            judge = "认为存在侧弯"
        else:
            judge = "不认为存在侧弯"
        self.present_output.setText(judge)

        # 打开并修改写入excel
        file_path = "E:\Internship\summer_pycharm\data.xlsx"
        app = xw.App(visible=True, add_book=False)
        wb = app.books.open(file_path)
        sht = xw.sheets.active
        sht.range('a1').value = ['ID', 'Name', 'Gender', 'Age', 'Height', 'Weight', 'Image', 'Result']
        objects = [input_id, input_name, input_gender, input_age, input_height, input_weight, fd, judge]
        rows = sht.used_range.last_cell.row  # 读取行数
        index = rows + 1
        sht.range(f'a{index}').value = objects  # 插入最新一行

        wb.save()
        wb.close()
        app.quit()

    def search(self): # 要求自动出现 不要点击按钮
        # 当line edit 不为空，打开excel
        if self.find_id.text() == "":
            pass
        else:
            file_path = "E:\Internship\summer_pycharm\data.xlsx"
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(file_path)
            sht = xw.sheets.active

            rows = sht.used_range.last_cell.row
            # 遍历所有行 判断是否符合id 是则显示该行信息
            for i in range(1, rows+1):
                current_id = sht.range(f"a{i}").value
                if current_id == self.find_id.text():
                    result_id, result_name, result_gender, result_age, result_height, result_weight, result_img_path, result_diagnose = sht.range(f"a{i}:h{i}").value

                    self.result_id.setText(f"{result_id}")
                    self.result_name.setText(f"{result_name}")
                    self.result_gender.setText(f"{result_gender}")
                    self.result_age.setText(f"{result_age}")
                    self.result_height.setText(f"{result_height}")
                    self.result_weight.setText(f"{result_weight}")
                    # 通过文件路径获取图片文件，并设置图片长宽为label控件的长款
                    img = QtGui.QPixmap(result_img_path).scaled(self.result_image.width(), self.result_image.height())
                    self.result_image.setPixmap(img)
                    self.result_diagnose.setText(f"{result_diagnose}")
                else:
                    pass
            wb.save()
            wb.close()
            app.quit()


if __name__ == '__main__':
    # 创建QApplication类的实例
    app = QApplication(sys.argv)
    # 创建一个主窗口
    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window.show()
    # 进入程序的主循环，并通过exit函数确保主循环安全结束
    sys.exit(app.exec_())
