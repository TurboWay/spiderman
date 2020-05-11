# spiderman
![](https://img.shields.io/badge/python-3.6%2B-brightgreen)
![](https://img.shields.io/badge/Scrapy-1.6%2B-orange)
![](https://img.shields.io/badge/scrapy--redis-0.6%2B-yellowgreen)
![](https://img.shields.io/badge/SQLAlchemy-1.3%2B-green)

基于scrapy-redis的通用分布式爬虫框架

### demo采集效果
![image](https://github.com/TurboWay/spiderman/blob/master/example/file.jpg)
![image](https://github.com/TurboWay/spiderman/blob/master/example/file_meta.jpg)
![image](https://github.com/TurboWay/spiderman/blob/master/example/list_data.jpg)

### 功能

- 自动建表
- 自动生成爬虫代码，只需编写少量代码即可完成分布式爬虫
- 自动存储元数据，分析统计和补爬都很方便
- 适合多站点开发，每个爬虫独立定制，互不影响
- 扩展简易，通过 job 生成初始请求，根据需要可以启用多个爬虫并行处理
- 采集数据落地方便，支持多种数据库
    - [x] mysql
    - [x] sqlserver
    - [x] oracle
    - [x] postgresql
    - [x] hbase
    - [x] sqlite3
    - [ ] mongodb
- 反爬处理简易，已封装各种反爬中间件
    - [x] 随机UserAgent
    - [x] 定制请求头Headers
    - [x] 定制Cookies
    - [x] 定制代理ip
    - [x] 在scrapy中使用requests
    - [x] Payload请求
    - [x] 使用Splash渲染 js


### 原理说明
1. 消息队列使用 redis，采集策略使用先进先出
2. 每个爬虫都有一个 job 文件，使用 job 来生成初始请求类 ScheduledRequest，并将其推送到 redis；
初始请求全部推到 redis 后，运行 spider 解析生成数据 并迭代新的请求到redis, 直到 redis 中的全部请求被消耗完
```python
# scrapy_redis请求类
class ScheduledRequest:

    def __init__(self, **kwargs):
        self.url = kwargs.get('url')                 # 请求url
        self.method = kwargs.get('method', 'GET')   # 请求方式 默认get
        self.callback = kwargs.get('callback')  # 回调函数，指定spider的解析函数
        self.body = kwargs.get('body')  # body, method为post时, 作为 post表单
        self.meta = kwargs.get('meta')  # meta, 携带反爬信息比如cookies，headers; 以及一些元数据，比如 pagenum
```


### 下载安装
1. pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requestsment.txt
2. 修改配置 spiderman/SP/settings.py
3. 运行demo示例

    cd spiderman；python SP_JOBS/zhifang_job.py


### 使用方法
新增爬虫时，运行 easy_scrapy.py 会根据模板自动生成以下代码文件，并自动在 pycharm 打开 spidername_job.py 文件；

| 类别 | 路径  | 说明  |
| ------------ | ------------ | ------------ |
| job       | SP_JOBS/spidername_job.py             | 编写初始请求 |
| spider    | SP/spiders/spidername.py              | 编写解析规则，产生新的请求  |
| items     | SP/items/spidername_items.py          | 定义字段  |
| pipelines | SP/pipelines/spidername_pipelines.py  | 定义表映射、字段类型  |

运行 SP_JOBS/spidername_job.py， 执行爬虫


### 注意事项
字段名称不能使用 isload、ctime、bizdate等字段，因为这些字段被作为通用字段，避免冲突


### TODO
- 支持更多类型的数据库，比如 mongodb
- 增加通用的补爬处理方法
- 增加分布式爬虫调用方法
- 增加 kafka 调用方法，实现实时采集、监控预警