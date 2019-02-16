# 拼多多爬虫

## 更新

### selenium 爬取被识别问题

在我发完这篇博客后，有很多朋友也尝试了我github上的代码。后来我发现，拼多多增加了一些反爬策略，我的代码已经被拼多多的反爬策略过滤了。作为一个好学的同学，我当然要深入研究一下啦。

首先，selenium+geckodriver 是通过模拟火狐浏览器访问的，以此欺骗目标网站就好像是人为点击的一样。可是当我再跑我的代码时，发现人工点击和selenium效果是不一样的，当使用selenium模拟时，不断会出现错误界面。经过查询，selenium在运行的时候会暴露出一些预定义的Javascript变量（特征字符串），例如"window.navigator.webdriver"，在非selenium环境下其值为undefined，而在selenium环境下，其值为true（如下图所示为selenium驱动下Chrome控制台打印出的值）。当然，还有其他很多变量，大家可以看看[这篇文章](http://www.site-digger.com/html/articles/20180821/653.html)。

那么我们重新理清思路，我们通过selenium模拟点击并连接代理，从代理中截取商品数据。而拼多多通过js文件判断我们是否使用selenium，并且将判断结果发送给服务器，控制返回内容。我们很难找到判断结果是以何种方式发送给服务器的。但我们可以从代理中截取该js文件，改变其内容，将判断selenium在js中预设的变量的部分删除掉就行了。

所以我在新代码中添加了一些代码：

```python
if 'react_psnl_verification_' in response.request.path:
	js_body = str(response.get_body_data(), 'utf-8')
	js_body =  js_body.replace("navigator.webdriver", "navigator.qwerasdfzxcv")
	response.set_body_data(bytes(js_body, 'utf-8'))
```

### 评论无法全部爬取问题

拼多多对于较多评论的商品只会展示部分，所以本项目只能爬取所有已知商品的可展示评论数据。



应最近一个项目需求，爬取拼多多数据。目前已经爬到90万+的商品数据。

## 目标

1. 所有商品。
2. 所有评论。
3. 附带的用户信息。
4. 项目需要用到的信息

## 已完成

1. 所有商品
2. 评论

## 所用依赖

​	拼多多没有网页端，爬取的是移动端搜索栏中的分类。因为是移动端，可以拿到返回商品的API，可是无法破解URL中的anticontent的字段，导致无法重放URL。综合以上特性所以就没有使用scrapy一类的框架。

​	商品的爬取是使用selenium结合代理，从代理中获取返回api中的商品信息。

​	代理使用的是@[qiyeboy](https://github.com/qiyeboy)的开源项目[BaseProxy]("https://github.com/qiyeboy/BaseProxy")

## 问题

### 验证码问题

​	经测验，访问次数到达一定的时候会出现验证码。普通orc识别效果并不好，选择使用了一种网络打码平台。优化访问后五六分钟一次验证码。









