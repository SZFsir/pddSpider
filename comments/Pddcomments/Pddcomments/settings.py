# -*- coding: utf-8 -*-

# Scrapy settings for Pddcomments project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Pddcomments'

SPIDER_MODULES = ['Pddcomments.spiders']
NEWSPIDER_MODULE = 'Pddcomments.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Pddcomments (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8000



# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1000000
#CONCURRENT_REQUESTS_PER_IP = 400

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'Pddcomments.middlewares.PddcommentsSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   #'Pddcomments.middlewares.PddcommentsDownloaderMiddleware': 543,
    'Pddcomments.middlewares.RandomHeaderMiddleware': 543,
    'Pddcomments.middlewares.HttpProxyMiddleware': 600,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'Pddcomments.pipelines.DuplicatePipeline': 100,
    'Pddcomments.pipelines.MongoDbPipeline': 301,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

TOKENS = [
    'JYLAMAHPPZRMP5QZ6BABDVKQKAIRJOEECLBKE3WVNDY473CL5PTA1020e0d',  # g
    '3STTXZVG5FLVGUYUJ74MWWK7PXRXWIHYGAQ4CMPJJXRP2KFHRCXQ102f17c',  # s1
    'VKUOQMMHBW6G5N334JIIZG4H65LQIQDTLMZHYMXIKJ64O3HBJASA100740d',  # s2
    'LB5KVDSJWI7JMMILBW6UVURM72JGUHYQITPWHVB2Q4HHWXC4I5WQ103b255',  # f
    '6KEX4JUWCQJHZTUD6DV65BTWATYQPI4SIPSA5FKNIWXFBRQY5PFQ101c635',  # l
    'NXJZHFYYREKXDWG3U3C4Y3K5FSQM24GRGELFTGCBAJU5KZK6RG6A102e759',  # h
    'MDY2BUSY6XNUYW63WP3T5QUJDKMISDAIPF2LSPKUFHXHY3GLAWVQ1020ab3'  # j
]

PROXY_URL = 'http://127.0.0.1'
CRAWL_URL = 'http://apiv3.yangkeduo.com/reviews/3256624378/list?page=1&size=10'
MONGO_URI = 'localhost'
MONGO_DB = 'PDDComments'

DOWNLOAD_TIMEOUT = 4
LOG_LEVEL = 'ERROR'
REACTOR_THREADPOOL_MAXSIZE = 20