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

### 分布式爬虫运行
![image](https://github.com/TurboWay/spiderman/blob/master/example/cluster.jpg)

### 单机爬虫运行
![image](https://github.com/TurboWay/spiderman/blob/master/example/standalone.jpg)

### 功能

- 自动建表
- 自动生成爬虫代码，只需编写少量代码即可完成分布式爬虫
- 自动存储元数据，分析统计和补爬都很方便
- 适合多站点开发，每个爬虫独立定制，互不影响
- 调用方便，可以根据传参自定义采集的页数以及启用的爬虫数量
- 扩展简易，可以根据需要选择采集模式，单机standalone(默认) 或者 分布式cluster
- 采集数据落地方便，支持多种数据库，只需在spider中启用相关的管道

    关系型
    - [x] mysql
    - [x] sqlserver
    - [x] oracle
    - [x] postgresql
    - [x] sqlite3
    
    非关系型
    - [x] hbase    
    - [x] mongodb
    
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

1. git clone https://github.com/TurboWay/spiderman.git; cd spiderman;
2. 【不使用虚拟环境的话，可以跳过步骤23】virtualenv -p /usr/bin/python3 --no-site-packages venv
3. 【不使用虚拟环境的话，可以跳过步骤23】source venv/bin/activate
4. pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requestsment.txt
5. 修改配置 vi SP/settings.py
6. 运行demo示例 python SP_JOBS/zhifang_job.py


### 快速开始（新增爬虫）

运行 easy_scrapy.py 会根据模板自动生成以下代码文件，并自动在 pycharm 打开 spidername_job.py 文件；

| 类别 | 路径  | 说明  |
| ------------ | ------------ | ------------ |
| job       | SP_JOBS/spidername_job.py             | 编写初始请求 |
| spider    | SP/spiders/spidername.py              | 编写解析规则，产生新的请求  |
| items     | SP/items/spidername_items.py          | 定义字段  |
| pipelines | SP/pipelines/spidername_pipelines.py  | 定义表映射、字段类型  |

直接执行 python SP_JOBS/spidername_job.py

或者动态传参（参数说明 -p 采集页数， -n 启用爬虫数量） python SP_JOBS/spidername_job.py -p 10 -n 1


### 快速开始（补爬）

运行 easy_scrapy.py 会根据模板自动生成以下代码文件，并自动在 pycharm 打开 spidername_job_patch.py 文件；

| 类别 | 路径  | 说明  |
| ------------ | ------------ | ------------ |
| job | SP_JOBS/spidername_job_patch.py  | 编写补爬请求 |

直接执行 python SP_JOBS/spidername_job_patch.py



### 分布式爬虫扩展

采集模式有两种(在 settings 控制)： 单机 standalone(默认) 和 分布式 cluster

如果想切换成分布式爬虫，需要在 spiderman/SP/settings.py 中启用以下配置

 <font color='red'>  注意：前提是 所有SLAVE机器的爬虫代码一致、python环境一致，都可以运行爬虫demo </font>

```python
# 采集模式 standalone 单机 (默认);  cluster 分布式 需要配置下方的 slaves
CRAWL_MODEL = 'cluster'
```

| 配置名称 | 意义  | 示例  |
| ------------ | ------------ | ------------ |
| SLAVES       | 【二选一】爬虫机器配置列表  | [{'host': '172.16.122.12', 'port': 22, 'user': 'spider', 'pwd': 'spider'}，<br>{'host': '172.16.122.13', 'port': 22, 'user': 'spider', 'pwd': 'spider'} ] |
| SLAVES_BALANCE | 【二选一】爬虫机器配置(ssh负载均衡) | {'host': '172.16.122.11', 'port': 2202, 'user': 'spider', 'pwd': 'spider'}  |
| SLAVES_ENV     | 【可选】爬虫机器虚拟环境路径  | /home/spider/workspace/spiderman/venv  |
| SLAVES_WORKSPACE | 【必填】爬虫机器代码工程路径  | /home/spider/workspace/spiderman  |


### 注意事项
字段名称不能使用 isload、ctime、bizdate等字段，因为这些字段被作为通用字段，避免冲突


### TODO
- ~~支持更多类型的数据库，比如 mongodb~~
- ~~增加通用的补爬处理方法~~
- ~~增加分布式爬虫调用方法~~
- 增加 kafka 调用方法，实现实时采集、监控预警
