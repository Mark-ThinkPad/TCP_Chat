# wxPython图形界面+TCP双向通信+多线程

## Content

<!-- TOC -->

- [wxPython图形界面+TCP双向通信+多线程](#wxpython图形界面tcp双向通信多线程)
    - [Content](#content)
    - [简介](#简介)
    - [文件内容](#文件内容)
    - [重要的技术实现](#重要的技术实现)
    - [相关资料](#相关资料)

<!-- /TOC -->

## 简介

- Python专选课上机任务之一, 使用wxPython制作GUI, 调用Python socket中的TCP模式进行双向通信, 
- 客户端和服务端都有可以使用的图形界面. 
- 部分核心代码源于兄弟项目: https://github.com/Mark-ThinkPad/TCP_Robot
- 开发环境: `Python 3.7.4`
- 系统环境: `Arch Linux`

## 文件内容

- [Server.py](./Server.py): 服务端核心代码, 已经抽象成类, 可以直接在终端中运行. 自动回复功能默认开启, 如果需要关闭, 则在 `Server` 类中找到 `chat()` 方法的最后一段, 注释掉复读机模式下的两行代码, 取消注释人工回复模式下两行的被注释代码. 
- [ChatServer.py](./ChatServer.py): 服务端的图形界面, 支持独立运行. 自动回复功能默认开启, 如果需要关闭, 则在 `ChatServer.py` 中找到 `RequestSync`线程子类中的最后一段代码, 根据注释提示操作即可.
- [Client.py](./Client.py): 客户端核心代码, 也抽象成类, 可以在终端中直接运行(请先启动服务端)
- [ChatClient.py](./ChatClient.py): 客户端的图形界面, 支持独立运行(请先启动服务端)
- [ChatUI.fbp](./ChatUI.fbp): wxFormBuilder的生成文件

## 重要的技术实现

- 消息持续刷新采用**多线程**来实现, 方法为编写自定义`threading.Thread`子类配合`wx.CallAfter()`, 实现消息的持续接收和消息刷新在图形界面上
- 客户端图形界面只用了一个自定义线程子类
- 服务端图形界面使用了**两个自定义线程子类, 而且是嵌套调用关系**

## 相关资料

- [Python Socket 编程详细介绍](https://gist.github.com/kevinkindom/108ffd675cb9253f8f71)
- [Python进阶开发之网络编程,socket实现在线聊天机器人](https://www.imooc.com/article/31228)
