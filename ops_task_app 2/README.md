# 运营任务地图 · 部署说明

## 文件结构
```
ops_task_app/
├── main.py          # 后端API服务
├── requirements.txt # Python依赖
├── start.sh         # 一键启动脚本
├── static/
│   └── index.html   # 前端页面
└── data/
    └── tasks.db     # 数据库（自动生成）
```

## 部署步骤（在服务器上操作）

### 第一步：上传文件
将整个 ops_task_app 文件夹上传到服务器，推荐放在 /home/ubuntu/ 或 /root/ 目录下。

上传方式：
- 使用 FTP 工具（如 FileZilla）
- 使用 scp 命令：scp -r ops_task_app/ root@你的服务器IP:/root/

### 第二步：在服务器上安装Python依赖
```bash
cd /root/ops_task_app
pip3 install -r requirements.txt
```

### 第三步：启动服务
```bash
bash start.sh
```

### 第四步：开放端口
在云服务器控制台（阿里云/腾讯云）的「安全组」里，添加入站规则：
- 协议：TCP
- 端口：8000
- 来源：0.0.0.0/0（允许所有人访问）

### 第五步：访问
浏览器打开：http://你的服务器公网IP:8000

---

## 后台常驻运行（可选）
如果想让服务在关闭终端后继续运行：

```bash
# 安装 screen
sudo apt install screen

# 创建新窗口并启动
screen -S opstask
bash start.sh

# 按 Ctrl+A 再按 D 退出窗口（服务继续运行）

# 下次查看日志
screen -r opstask
```

## 数据备份
数据存在 data/tasks.db 文件中，定期下载备份即可。

## 常见问题
- 端口已被占用：修改 start.sh 最后一行的 8000 为其他端口号
- 访问不了：检查安全组端口是否已开放
- 数据丢失：不要删除 data/tasks.db 文件
