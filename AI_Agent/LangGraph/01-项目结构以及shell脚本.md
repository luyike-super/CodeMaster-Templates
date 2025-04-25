# 目录结构  ， 后面有一键shell(powershell)脚本

```
project_root/
│
├── .env                      # 环境变量配置文件
├── .gitignore                # Git忽略文件
├── pyproject.toml            # 现代Python项目配置
├── README.md                 # 项目文档说明
│
├── app/                      # 主应用程序包
│   ├── __init__.py           # 包初始化文件
│   ├── main.py               # FastAPI应用程序入口点
│   ├── config.py             # 应用程序配置
│   │
│   ├── api/                  # API端点
│   │   ├── __init__.py
│   │   ├── deps.py           # API依赖项(认证等)
│   │   ├── v1/               # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── router.py     # 主v1路由器
│   │   │   ├── endpoints/    # API端点
│   │   │       ├── __init__.py
│   │   │       ├── users.py  # 用户相关接口
│   │   │       ├── items.py  # 物品相关接口
│   │   │       └── ...
│   │
│   ├── core/                 # 核心应用功能
│   │   ├── __init__.py
│   │   ├── security.py       # 安全工具
│   │   ├── exceptions.py     # 自定义异常
│   │   └── logging.py        # 日志配置
│   │
│   ├── db/                   # 数据库相关代码
│   │   ├── __init__.py
│   │   ├── session.py        # 数据库会话管理
│   │   ├── base.py           # 基础模型类
│   │   └── init_db.py        # 数据库初始化
│   │
│   ├── models/               # ORM模型
│   │   ├── __init__.py
│   │   ├── user.py           # 用户模型
│   │   ├── item.py           # 物品模型
│   │   └── ...
│   │
│   ├── schemas/              # Pydantic模式（请求/响应）
│   │   ├── __init__.py
│   │   ├── user.py           # 用户数据模式
│   │   ├── item.py           # 物品数据模式
│   │   └── ...
│   │
│   ├── services/             # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── user_service.py   # 用户服务
│   │   └── ...
│   │
│   ├── scrapers/             # 网络爬虫模块
│   │   ├── __init__.py
│   │   ├── base_scraper.py   # 基础爬虫类
│   │   ├── website_a.py      # 网站A爬虫
│   │   ├── website_b.py      # 网站B爬虫
│   │   └── ...
│   │
│   ├── clients/              # 第三方API客户端
│   │   ├── __init__.py
│   │   ├── base_client.py    # 基础API客户端
│   │   ├── service_a_client.py  # 服务A客户端
│   │   ├── service_b_client.py  # 服务B客户端
│   │   └── ...
│   │
│   └── langgraph/            # LangGraph组件
│       ├── __init__.py
│       ├── graphs/           # LangGraph图定义
│       │   ├── __init__.py
│       │   ├── main_graph.py # 主图
│       │   └── ...
│       ├── nodes/            # LangGraph节点
│       │   ├── __init__.py
│       │   ├── data_processor.py  # 数据处理节点
│       │   ├── llm_node.py   # 语言模型节点
│       │   └── ...
│       ├── states/           # 状态定义
│       │   ├── __init__.py
│       │   ├── base_state.py # 基础状态类
│       │   └── ...
│       └── utils/            # LangGraph工具
│           ├── __init__.py
│           └── ...
│
├── migrations/               # 数据库迁移
│   ├── versions/             # 迁移版本
│   │   └── ...
│   ├── env.py                # 迁移环境
│   ├── README                # 迁移说明
│   ├── script.py.mako        # 迁移脚本模板
│   └── alembic.ini           # Alembic配置
│
├── tests/                    # 测试套件
│   ├── __init__.py
│   ├── conftest.py           # 测试固件
│   ├── test_api/             # API测试
│   │   ├── __init__.py
│   │   ├── test_users.py     # 用户API测试
│   │   └── ...
│   ├── test_services/        # 服务测试
│   │   ├── __init__.py
│   │   └── ...
│   └── test_langgraph/       # LangGraph测试
│       ├── __init__.py
│       └── ...
│
├── scripts/                  # 实用脚本
│   ├── seed_db.py            # 数据库种子数据
│   └── ...
│
└── docs/                     # 文档
    ├── index.md              # 文档索引
    └── ...
```

# 一键shell脚本  (保存为： create_project_structure.ps1 )
```
# Create project structure PowerShell script

# Set project root directory
$projectRoot = "project_root"

# Create project root directory (if it doesn't exist)
if (!(Test-Path $projectRoot)) {
    New-Item -Path $projectRoot -ItemType Directory
}

# Create root directory files
$rootFiles = @(
    ".env",
    ".gitignore",
    "pyproject.toml",
    "README.md"
)

foreach ($file in $rootFiles) {
    New-Item -Path "$projectRoot\$file" -ItemType File -Force
}

# Create directory structure
$directories = @(
    "app",
    "app\api",
    "app\api\v1",
    "app\api\v1\endpoints",
    "app\core",
    "app\db",
    "app\models",
    "app\schemas",
    "app\services",
    "app\scrapers",
    "app\clients",
    "app\langgraph",
    "app\langgraph\graphs",
    "app\langgraph\nodes",
    "app\langgraph\states",
    "app\langgraph\utils",
    "migrations",
    "migrations\versions",
    "tests",
    "tests\test_api",
    "tests\test_services",
    "tests\test_langgraph",
    "scripts",
    "docs"
)

foreach ($dir in $directories) {
    New-Item -Path "$projectRoot\$dir" -ItemType Directory -Force
}

# Create app directory files
$appFiles = @(
    "app\__init__.py",
    "app\main.py",
    "app\config.py",
    "app\api\__init__.py",
    "app\api\deps.py",
    "app\api\v1\__init__.py",
    "app\api\v1\router.py",
    "app\api\v1\endpoints\__init__.py",
    "app\api\v1\endpoints\users.py",
    "app\api\v1\endpoints\items.py",
    "app\core\__init__.py",
    "app\core\security.py",
    "app\core\exceptions.py",
    "app\core\logging.py",
    "app\db\__init__.py",
    "app\db\session.py",
    "app\db\base.py",
    "app\db\init_db.py",
    "app\models\__init__.py",
    "app\models\user.py",
    "app\models\item.py",
    "app\schemas\__init__.py",
    "app\schemas\user.py",
    "app\schemas\item.py",
    "app\services\__init__.py",
    "app\services\user_service.py",
    "app\scrapers\__init__.py",
    "app\scrapers\base_scraper.py",
    "app\scrapers\website_a.py",
    "app\scrapers\website_b.py",
    "app\clients\__init__.py",
    "app\clients\base_client.py",
    "app\clients\service_a_client.py",
    "app\clients\service_b_client.py",
    "app\langgraph\__init__.py",
    "app\langgraph\graphs\__init__.py",
    "app\langgraph\graphs\main_graph.py",
    "app\langgraph\nodes\__init__.py",
    "app\langgraph\nodes\data_processor.py",
    "app\langgraph\nodes\llm_node.py",
    "app\langgraph\states\__init__.py",
    "app\langgraph\states\base_state.py",
    "app\langgraph\utils\__init__.py"
)

foreach ($file in $appFiles) {
    New-Item -Path "$projectRoot\$file" -ItemType File -Force
}

# Create migrations directory files
$migrationsFiles = @(
    "migrations\env.py",
    "migrations\README",
    "migrations\script.py.mako",
    "migrations\alembic.ini"
)

foreach ($file in $migrationsFiles) {
    New-Item -Path "$projectRoot\$file" -ItemType File -Force
}

# Create tests directory files
$testsFiles = @(
    "tests\__init__.py",
    "tests\conftest.py",
    "tests\test_api\__init__.py",
    "tests\test_api\test_users.py",
    "tests\test_services\__init__.py",
    "tests\test_langgraph\__init__.py"
)

foreach ($file in $testsFiles) {
    New-Item -Path "$projectRoot\$file" -ItemType File -Force
}

# Create scripts directory files
$scriptsFiles = @(
    "scripts\seed_db.py"
)

foreach ($file in $scriptsFiles) {
    New-Item -Path "$projectRoot\$file" -ItemType File -Force
}

# Create docs directory files
$docsFiles = @(
    "docs\index.md"
)

foreach ($file in $docsFiles) {
    New-Item -Path "$projectRoot\$file" -ItemType File -Force
}

Write-Host "Project structure creation completed!"

```

