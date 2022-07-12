from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
import os,sys
from PyQt5.QtCore import QThread,Qt
import pymysql

#引入本地库
root_folder32 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder32=os.path.dirname(root_folder32 )
resources_folder32=os.path.join(parent_folder32,'resources')
sys.path.append(parent_folder32)
sys.path.append(os.path.join(parent_folder32,'gui'))
from log_form import logForm

class log_widget(QWidget, logForm):
    def __init__(self):
        super(log_widget, self).__init__()

        # 子窗口初始化时实现子窗口布局
        self.ui = logForm()
        self.ui.setupUi(self)
        self.initConstant()
        self.initUI()
        # 设置子窗体最小尺寸
        # self.setMinimumWidth(30)
        # self.setMinimumHeight(30)

    def initConstant(self):
        self.head_img=os.path.join(resources_folder32,'default_head.png') #头像
        self.username=None#用户名
        self.password=None#密码
        self.log_status=0#登录状态：０为未登录,１为已登录
        #连接mysql数据库
        #如果你不是本地mysql你可以将localhost换成你远程服务器的IP地址
        self.conn=pymysql.connect(host='localhost', port=3306, user='wjy', passwd='123456',db='vosinfo',charset='utf8')
        self.cursor=self.conn.cursor()

    def initUI(self):
        #****************头像设置****************
        head_pix=QPixmap(self.head_img)
        self.ui.label_head.setPixmap(head_pix)
        self.ui.label_head.chooseHeadSignal.connect(self.chooseHead)

        #*****************line＿edit*************
        # 设置占位符
        self.ui.lineEdit_password.setPlaceholderText("password")
        self.ui.lineEdit_username.setPlaceholderText("username")

        #***********按钮点击事件*****************
        self.ui.pushButton_login.clicked.connect(self.log_in)
        self.ui.pushButton_logout.clicked.connect(self.log_out)
        self.ui.pushButton_register.clicked.connect(self.register)

        #********************qss美化****************
        self.stylesheet=[]
        self.stylesheet.append('QLabel{font-family:Microsoft Yahei;font-size:12px;}')
        self.stylesheet.append('QLineEdit{font-family:Microsoft Yahei;font-size:15px;font-weight:bold;}')
        # self.ui.horizontalLayout.setStyleSheet(''.join(self.stylesheet))
        self.setStyleSheet(''.join(self.stylesheet))

    def chooseHead(self):
        filename_choose,filetype=QFileDialog.getOpenFileName(self,"选择头像",'/home/wanwanvv/图片',"Image files(*.jpg *.png *.jpeg)")
        if filename_choose!="":
            self.load_img(filename_choose)
        self.head_img=filename_choose

    # 加载图片并显示到label中
    def load_img(self, img_path):
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            return

        img = QImage.fromData(img_data)
        if img.isNull():
            QMessageBox.warning(self, 'Warning', 'Invalid Image')
            return False
        pixmap = QPixmap.fromImage(img)
        pixmap = pixmap.scaled(int(self.ui.label_head.width()),int(self.ui.label_head.height()), Qt.KeepAspectRatio)
        # print(pixmap.size())
        self.ui.label_head.setPixmap(pixmap)

    def checkValues_register(self):
        username = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()
        if not username:  # 用户名为空
            QMessageBox.information(self, 'Error', '用户名不能为空!', QMessageBox.Ok)
            return False
        elif not password:  # 如果有一个密码或者密码确认框为空
            QMessageBox.information(self, 'Error', '密码不能为空!', QMessageBox.Ok)
            return False
        elif self.is_has(username):  # 如果用户名已经存在
            QMessageBox.information(self, 'Error', '用户名已经存在!', QMessageBox.Ok)
            return False
        else:
            self.username=username
            self.password=password
            return True

    def checkValues_log(self):
        username = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()
        if not username:  # 用户名为空
            QMessageBox.information(self, 'Error', '用户名不能为空!', QMessageBox.Yes)
            return False
        elif not password:  # 如果有一个密码或者密码确认框为空
            QMessageBox.information(self, 'Error', '密码不能为空!', QMessageBox.Yes)
            return False

        else:
            self.username=username
            self.password=password
            return True

    def is_has(self,username):
        """判断数据库中是否含有用户名"""
        sql = 'SELECT * FROM users WHERE username=%s'
        result = self.cursor.execute(sql, [username])  # 执行sqlite语句
        self.conn.commit()
        #data = result.fetchall()  # 获取所有的内容
        if result!=0:
            return True
        else:
            return False

    def log_in(self):
        check_result=self.checkValues_log()
        if check_result:
            sql = 'SELECT username, password FROM users WHERE username=%s'  # 从数据库中读取数据
            result = self.cursor.execute(sql, [self.username])
            print('select result:')
            print(result)
            if result!=0:
                data = self.cursor.fetchall()
                if str(data[0][1]) == self.password:
                    QMessageBox.information(self, 'Successfully', '登录成功! \n Welcome {}'.format(self.username),
                                            QMessageBox.Ok)
                    self.log_status=1
                    self.ui.lineEdit_status.setText("已登录")
                else:
                    QMessageBox.information(self, 'Failed', '密码错误,请重新输入!',
                                            QMessageBox.Ok)

            else:
                QMessageBox.information(self, 'Error', '没有此用户,请先注册！', QMessageBox.Ok)

    def log_out(self):
        reply = QMessageBox.question(self, 'Message', '确定要退出当前帐号吗？', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.head_img = os.path.join(resources_folder32, 'default_head.png')  # 头像
            head_pix = QPixmap(self.head_img)
            self.ui.label_head.setPixmap(head_pix)
            self.username = None  # 用户名
            self.password = None  # 密码
            self.log_status = 0  # 登录状态：０为未登录,１为已登录
            self.ui.lineEdit_status.setText('未登录')
            self.ui.lineEdit_password.setText('')
            self.ui.lineEdit_username.setText('')
            self.ui.lineEdit_password.setPlaceholderText("password")
            self.ui.lineEdit_username.setPlaceholderText("username")
        else:
            return


    def register(self):
        check_result=self.checkValues_register()
        if check_result:
            sqlstring = 'insert into users(username, password) values(%s,%s)'  # 添加入数据库
            self.cursor.execute(sqlstring,[self.username, self.password])
            self.conn.commit()
            # sql = "select aid,sum(dollars) from orders where cid=%s group byaid"
            # self.cursor.execute(sql, [agent])
            QMessageBox.information(self, 'Successfully', '注册成功!'.format(self.username),QMessageBox.Ok)


