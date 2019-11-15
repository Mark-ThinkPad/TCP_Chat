# -*- coding: utf-8 -*-
# 此程序为Client客户端
import wx
import wx.xrc
import time
import threading
from Client import Client


class MyFrame1(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"聊天界面", pos=wx.DefaultPosition,
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

        # 建立客户端对象
        self.client = Client()
        # 多线程走起
        self.thread = ResponseSync(self)
        self.thread.start()

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    # 关闭窗口时发送强制关闭的消息
    def close(self, event):
        dlg = wx.MessageDialog(None, '是否关闭聊天客户端', '关闭提示', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.client.force_close()
            dlg.Destroy()
            self.Destroy()

    def click(self, event):
        input_str = self.m_textCtrl1.GetValue()
        if input_str:
            self.m_textCtrl2.AppendText(
                "【我】" + " " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n' + input_str + '\n\n')
            self.client.send_msg_gui(input_str)
        else:
            wx.MessageDialog(None, '未输入任何字符!', '警告', wx.OK | wx.ICON_WARNING).ShowModal()
        self.m_textCtrl1.Clear()

    def fresh(self, event):
        pass


class ResponseSync(threading.Thread):
    def __init__(self, window: MyFrame1):
        super(ResponseSync, self).__init__()
        self.window = window

    def run(self) -> None:
        while True:
            res = self.window.client.rec_msg_gui()
            if res == '与服务器意外断开连接' or res == '与服务器断开连接':
                # 发出断开连接的信号之后停止执行
                wx.CallAfter(self.window.m_textCtrl2.AppendText, res)
                break
                # 发出信号
            elif res:
                res = "【人工智障聊天机器人】" + " " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n' + res + '\n\n'
                wx.CallAfter(self.window.m_textCtrl2.AppendText, res)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame1(None)
    frame.Show()
    app.MainLoop()
