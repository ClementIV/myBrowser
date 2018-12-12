from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from ui import Ui_MainWindow
import requests
from pyquery import PyQuery as pq
import sys


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # 设置窗口标题
        self.setWindowTitle('My Browser 2120180451 冯永琦')
        # 设置窗口图标
        self.setWindowIcon(QIcon('icons/penguin.png'))
        self.show()
        #
        # 添加 URL 地址栏
        self.urlbar = QLineEdit()
        # 让地址栏能响应回车按键信号
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        #
        # 添加标签栏
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.add_new_tab(QUrl('http://baidu.com'), 'Homepage')
        # new_tab_action = QAction(QIcon('icons/add_page.png'), 'New Page', self)
        # new_tab_action.triggered.connect(self.add_new_tab)
        self.setCentralWidget(self.tabs)

        new_tab_action = QAction(QIcon('icons/add_page.png'), 'New Page', self)
        new_tab_action.triggered.connect(self.add_new_page)

        #
        # 添加导航栏
        navigation_bar = QToolBar('Navigation')
        # # 设定图标的大小
        navigation_bar.setIconSize(QSize(16, 16))
        self.addToolBar(navigation_bar)
        #
        # 添加前进、后退、停止加载和刷新的按钮
        back_button = QAction(QIcon('icons/back.png'), 'Back', self)
        next_button = QAction(QIcon('icons/next.png'), 'Forward', self)
        stop_button = QAction(QIcon('icons/cross.png'), 'stop', self)
        reload_button = QAction(QIcon('icons/renew.png'), 'reload', self)

        back_button.triggered.connect(self.tabs.currentWidget().back)
        next_button.triggered.connect(self.tabs.currentWidget().forward)
        stop_button.triggered.connect(self.tabs.currentWidget().stop)
        reload_button.triggered.connect(self.tabs.currentWidget().reload)

        # 将按钮添加到导航栏上
        navigation_bar.addAction(back_button)
        navigation_bar.addAction(next_button)
        navigation_bar.addAction(stop_button)
        navigation_bar.addAction(reload_button)
        #
        navigation_bar.addSeparator()
        navigation_bar.addAction(new_tab_action)

        #
        navigation_bar.addSeparator()

        # 添加GET HEAD按钮
        get_button = QAction(QIcon('icons/GET.png'), 'GET', self)
        head_button = QAction(QIcon('icons/HEAD.png'), 'HEAD', self)

        get_button.triggered.connect(self.get_request)
        head_button.triggered.connect(self.head_request)
        navigation_bar.addAction(get_button)
        navigation_bar.addAction(head_button)

        navigation_bar.addSeparator()

        # # 添加地址栏
        navigation_bar.addWidget(self.urlbar)

    # HEAD 请求
    def head_request(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        response = requests.head(q.toString())

        text_brower = QTextBrowser()
        text_brower.setText(str(response.headers))
        self.tabs.addTab(text_brower, 'HEAD-'+str(response.status_code))
        # url
        self.urlbar.setText(q.toString())

    # GET 请求
    def get_request(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        response = requests.get(q.toString())

        # 解析html
        text_brower = QTextBrowser()
        content = pq(response.content)
        text_brower.setText(content.text())
        self.tabs.addTab(text_brower, 'GET-' + content('title').text())
        #url
        self.urlbar.setText(q.toString())

    # 响应回车按钮，将浏览器当前访问的 URL 设置为用户输入的 URL
    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        self.tabs.currentWidget().setUrl(q)

    def renew_urlbar(self, q, browser=None):
        # 如果不是当前窗口所展示的网页则不更新 URL
        if browser != self.tabs.currentWidget():
            return
        # 将当前网页的链接更新到地址栏
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def add_new_page(self):
        self.add_new_tab()

    # 添加新的标签页
    def add_new_tab(self, qurl=QUrl(''), label='Blank'):
        # 为标签创建新网页
        browser = QWebEngineView()
        browser.page().load(qurl)
        i = self.tabs.addTab(browser, label)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.renew_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def slotSourceDownloaded(self, browser):
        # reply = self.sender()
        self.textEdit = QTextEdit()
        self.textEdit.setAttribute(Qt.WA_DeleteOnClose)
        # self.adjustSize()
        self.textEdit.resize(600, 400)
        self.textEdit.move(self.geometry().center() - self.textEdit.rect().center())
        # self.textEdit.show()
        browser.page().toHtml(self.textEdit.setPlainText)
        self.tabs.addTab(self.textEdit, browser.page().title())

    # 双击标签栏打开新页面
    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    #
    def current_tab_changed(self, i):
        qurl = QUrl( self.urlbar.text())
        self.renew_urlbar(qurl, self.tabs.currentWidget())

    def close_current_tab(self, i):
        # 如果当前标签页只剩下一个则不关闭
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)


# 创建应用
app = QApplication(sys.argv)
# 创建主窗口
window = MainWindow()
# 显示窗口
window.show()
# 运行应用，并监听事件
app.exec_()
