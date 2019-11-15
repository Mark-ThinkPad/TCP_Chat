# -*- coding: utf-8 -*-
# 此程序为Server服务端
import wx
import wx.xrc
import time
import threading
from Server import Server


class MyFrame1(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"服务端界面", pos=wx.DefaultPosition,
                          size=wx.Size(600, 600), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_textCtrl2 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(600, 400),
                                       wx.TE_MULTILINE | wx.TE_READONLY)
        bSizer1.Add(self.m_textCtrl2, 0, wx.ALL, 5)

        self.m_textCtrl1 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(600, 100),
                                       wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        bSizer1.Add(self.m_textCtrl1, 0, wx.ALL, 5)

        self.m_button = wx.Button(self, wx.ID_ANY, u"发送消息", wx.DefaultPosition, wx.Size(600, 30), 0)
        bSizer1.Add(self.m_button, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.m_timer = wx.Timer()
        self.m_timer.SetOwner(self, wx.ID_ANY)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.close)
        self.m_textCtrl1.Bind(wx.EVT_TEXT_ENTER, self.click)
        self.m_button.Bind(wx.EVT_BUTTON, self.click)
        self.Bind(wx.EVT_TIMER, self.fresh, id=wx.ID_ANY)

        # 建立服务端端对象
        self.server = Server()
        self.m_textCtrl2.AppendText('正在监听 ' + self.server.bind_addr + '\n')
        # 多线程走起
        self.thread = StayAccept(self)
        self.thread.start()

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    # 关闭窗口时发送强制关闭的消息
    def close(self, event):
        dlg = wx.MessageDialog(None, '是否关闭服务端', '关闭提示', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.server.socket.close()
            dlg.Destroy()
            self.Destroy()

    def click(self, event):
        input_str = self.m_textCtrl1.GetValue()
        if input_str:
            try:
                self.server.conn_socket.sendall(('(手动回复): ' + input_str).encode('utf-8'))
                print('(手动回复):', input_str)
                self.m_textCtrl2.AppendText('(手动回复): ' + input_str + '\n')
            except BrokenPipeError:
                self.m_textCtrl2.AppendText(str(self.server.addr) + ' 意外断开\n' + '已关闭相应的socket连接\n\n')
                print(self.server.addr, '意外断开')
                print('已关闭相应的socket连接\n')
                self.thread.rs.terminate()
                self.server.conn_socket.close()
        else:
            wx.MessageDialog(None, '未输入任何字符!', '警告', wx.OK | wx.ICON_WARNING).ShowModal()
        self.m_textCtrl1.Clear()

    def fresh(self, event):
        pass


class StayAccept(threading.Thread):
    def __init__(self, window: MyFrame1):
        super(StayAccept, self).__init__()
        self.window = window
        self.rs = None

    def run(self) -> None:
        while True:
            self.window.server.conn_socket, self.window.server.addr = self.window.server.socket.accept()
            new_conn_info = '连接地址: ' + str(self.window.server.addr)
            print(new_conn_info)
            wx.CallAfter(self.window.m_textCtrl2.AppendText, new_conn_info + '\n')
            # 自动回复模式
            self.rs = RequestSync(self.window)
            self.rs.start()


# 沙雕回复语料库
keywords = {'你是谁': '我是人工智障聊天机器人',
            '今天天气如何': '荆州的天气可说不准呢',
            '现在几点': '不要逗我了, 你电脑的任务栏上一眼就可以看到时间',
            '吃饭了吗': '吃吃吃就知道吃',
            '你昨天几点睡的': '真正的强者不需要睡觉',
            '阿米娅是兔子还是驴': '是驴',
            '我想睡觉': 'Doctor, 您现在还不能休息呢',
            '奥尔加团长': '不要停下来啊',
            'PHP': 'PHP是世界上最好的语言',
            'Python': 'Python可能是世界上最好......学的语言',
            'CSS': '天下苦CSS久矣',
            '关机': '本人工智障暂时没有执行 shutdown now 的权限',
            '于谦三大爱好': '抽烟喝酒烫头',
            '相声四门功课': '吃喝抽烫, 脱鞋就唱, 刀枪棍棒, 斧钺钩叉',
            }


class RequestSync(threading.Thread):
    def __init__(self, window: MyFrame1):
        super(RequestSync, self).__init__()
        self.window = window
        self._running = True

    def terminate(self):
        self._running = False

    def run(self) -> None:
        self.window.server.conn_socket.sendall('你好, 人工智障聊天机器人为您服务, 输入 exit 即可退出聊天'.encode('utf-8'))
        while self._running:
            try:
                data = self.window.server.conn_socket.recv(1024).decode('utf-8')
            except ConnectionResetError:
                self.window.server.conn_socket.close()
                disconnect_info = str(self.window.server.addr) + ' 意外断开\n'
                print(disconnect_info)
                wx.CallAfter(self.window.m_textCtrl2.AppendText, disconnect_info)
                break
            if data == 'exit':
                self.window.server.conn_socket.sendall('exit'.encode('utf-8'))
                self.window.server.conn_socket.close()
                disconnect_info = str(self.window.server.addr) + ' 结束对话\n'
                print(disconnect_info)
                wx.CallAfter(self.window.m_textCtrl2.AppendText, disconnect_info)
                break
            if data == 'force_exit':
                self.window.server.conn_socket.close()
                disconnect_info = str(self.window.server.addr) + ' 结束对话\n'
                print(disconnect_info)
                wx.CallAfter(self.window.m_textCtrl2.AppendText, disconnect_info)
                break
            if data:
                msg = '来自 '+str(self.window.server.addr)+' '+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+' 的消息: '+data
                print(msg)
                wx.CallAfter(self.window.m_textCtrl2.AppendText, msg + '\n')
                # 下面是自动回复功能, 若想关闭请直接注释掉
                if data in keywords:
                    res = '(命中词库): ' + keywords[data]
                    self.window.server.conn_socket.sendall(res.encode('utf-8'))
                    print(res)
                    wx.CallAfter(self.window.m_textCtrl2.AppendText, res + '\n')
                else:
                    # 复读机模式
                    res = '(复读机模式): ' + data
                    self.window.server.conn_socket.sendall(res.encode('utf-8'))
                    print(res)
                    wx.CallAfter(self.window.m_textCtrl2.AppendText, res + '\n')


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame1(None)
    frame.Show()
    app.MainLoop()
