# Graph Memory Visualizer

graph-memory 知识图谱记忆可视化工具

## 功能特性

- 📊 **可视化展示**：将知识图谱以网络图形式展示
- 🔍 **搜索功能**：支持按节点名称搜索
- 📋 **详情查看**：点击节点查看详情和相关关系
- 📈 **统计信息**：显示节点数、关系数、社区数
- 🎨 **美观界面**：深蓝色+金色高端风格，响应式设计

## 快速启动

```bash
# 克隆项目（或上传文件到你的服务器）
cd graph-memory-viewer
python3 server.py
```

## 项目结构

```
graph-memory-viewer/
├── index.html      # 前端页面
├── server.py       # Python 后端服务（读取 SQLite 数据库）
└── README.md       # 说明文档
```

## 数据库路径

本仓库已经包含完整的 `graph-memory.db` 数据库文件（克隆后自动获得）。

后端优先读取当前目录的 `graph-memory.db`，如果找不到再读取 `~/.openclaw/graph-memory.db`。

如果你想使用你自己新的数据库，替换当前目录的 `graph-memory.db` 文件即可。

## 访问地址

启动后访问：`http://<your-server-ip>:8888`

如果你用 Nginx 反向代理，可以参考这个配置：

```nginx
server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 依赖

只需要 Python 3.x，不需要额外安装依赖（使用标准库）。
