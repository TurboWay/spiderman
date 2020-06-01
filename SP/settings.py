# -*- coding: utf-8 -*-

# Scrapy settings for SP project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

# 日志
LOGDIR = 'D:/GitHub/spiderman/SP_log'  # /home/spider/workspace/spiderman/SP_log

# 附件存放目录
FILES_STORE = 'D:/GitHub/spiderman/Files'  # /home/spider/workspace/spiderman/Files

BOT_NAME = 'SP'

SPIDER_MODULES = ['SP.spiders']
NEWSPIDER_MODULE = 'SP.spiders'

# redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# splash服务url
SPLASH_URL = 'http://127.0.0.1:8050'

# bucketsize 入库批次大小，每100条入库一次
BUCKETSIZE = 100

# 爬虫 meta
META_ENGION = 'sqlite:///meta.db'

# rdbms
ENGION_CONFIG = [
    # 'mysql://user:pwd@127.0.0.1:3306/spider_db?charset=utf8',  # mysql
    # 'postgresql://user:pwd@127.0.0.1:5432/spider_db',  # postgresql
    # 'oracle://user:pwd@127.0.0.1:1521/spider_db',  # oracle
    # 'mssql+pymssql://user:pwd@127.0.0.1:1433/spider_db',  # sqlserver
    'sqlite:///D:/GitHub/spiderman/foo.db'  # sqlite
][0]

# hbase
HBASE_HOST = '172.16.122.20'
HBASE_PORT = 25002

# mongodb
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DB = 'spider_db'

# elasticsearch
ES_SERVERS = ['127.0.0.1:9200', ]

# kafka
KAFKA_SERVERS = ['172.16.122.17:9092', ]

# 采集模式
CRAWL_MODEL = 'standalone'  # standalone 单机 (默认) ; cluster分布式, 需要配置下方的 slaves

# 爬虫slaves配置, SLAVES_BALANCE 和 SLAVES 取一个即可；建议配合 nginx 或者 haproxy, 做个 ssh 的负载均衡
SLAVES = [
    # {'host': '172.16.122.11', 'port': 22, 'user': 'spider', 'pwd': 'spider'},
    # {'host': '172.16.122.12', 'port': 22, 'user': 'spider', 'pwd': 'spider'},
    # {'host': '172.16.122.13', 'port': 22, 'user': 'spider', 'pwd': 'spider'},
    # {'host': '172.16.122.14', 'port': 22, 'user': 'spider', 'pwd': 'spider'}
]
SLAVES_BALANCE = {
    # 'host': '172.16.122.11', 'port': 2202, 'user': 'spider', 'pwd': 'spider'
}  # ssh 负载均衡
SLAVES_ENV = '/home/spider/workspace/spiderman/venv'  # slave 虚拟环境路径, 如果有用虚拟环境的话 like /home/spider/workspace/venv
SLAVES_WORKSPACE = '/home/spider/workspace/spiderman'  # slave 爬虫代码工程路径 like /home/spider/workspace/spiderman/SP

# scrapy_redis
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = False

MYEXT_ENABLED = True  # 开启扩展
IDLE_NUMBER = 3  # 配置空闲持续时间单位为 默认2个 ，一个时间单位为5s；这边设置3，即 15s无任务，爬虫关闭

# 在 EXTENSIONS 配置，激活扩展
EXTENSIONS = {
    'SP.scrapy_redis_extensions.RedisSpiderSmartIdleClosedExensions': 500,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# retry setting
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 400, 403, 404]

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'SP.middlewares.SPSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#     # 'GF.middlewares.GfDownloaderMiddleware': 543,
#     'SP.middlewares.UserAgentMiddleWare.UserAgentMiddleWare': 200,
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': 300
# }


# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'SP.pipelines.SPPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
