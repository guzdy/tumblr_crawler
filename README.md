Tumblr_Crawler
==============

这是一个用于下载指定的 Tumblr 博客图片和视频的 Python 脚本。

<br />

环境安装
-------

配置 Python3 环境(Python2下没有测试过)，然后打开命令行模式，输入如下命令。

```shell
$ git clone git@github.com:guzdy/lofter_crawler.git
$ cd lofter-crawler
$ pip install -r requirements.txt
```


配置和运行
---------

有两种方式来指定你要下载的博客，一是编辑"config.ini"，二是指定命令行参数。
<br />

#### 第一种方法:编辑"config.ini"文件

用文字编辑器软件，打开文件"config.ini"，把你想要下载的博客编辑进去，样式如下:


[USER]
BLOGNAME = zenglinghua329 karolina-dean


其中：
1. [DEFAULT] 为默认配置， [USER] 为用户配置部分。
2. "BLOGNAME = " 后面输入一个或多个博客名，以空格分离。
   如上面设置将下载 loftermeirenzhi.lofter.com ; cxy722.lofter.com 的内容。
3. "TIMEOUT" 和 "TIMESLEEP" 分别为下载等待响应时间和下载每页后的等待时间（单位：秒）。
   TIMESLEEP 作为一种反爬手段，用处可能不如设置 ProxyIP 大。
4. 如果需要设置代理，与 [SAMPLE] 中的设置类似方法设置即可，[SAMPLE] 中为 XX-NET/GOAGENT 代理。
   当然也可通过购买 VPS 设置 shadowsocks 全局配置方法，就无需设置代理了。

在命令行中，输入 `python lofter_crawler.py`
**当然 Windows 用户也可以直接双击 'start.bat' 启动程序。**
<br />

#### 第二种方法:使用命令行参数

更直接的方式是，直接用命令行。

```shell
$ python lofter_crawler.py -b blogname1 [-b blogname2]
```

每个博客名下， 需加入 "-b" 参数。
<br />

下载内容样式
-----------

程序运行后,会在当前路径下生成一个跟博客名相同的文件夹，图片/视频都会放在这个文件夹下面。
文件名取名有两种方式：
1. 相应的博客页面内容的前十字。
2. 在 Tumblr 服务器中的名字。
3. 照片/视频选最高规格模式。

多次运行这个脚本，不会重复下载已经下载过的图片和视频。

另外也会在文件夹下，生成一个文本记录具体的照片下载路径，Tags, 博客内容文本。

<br />

### 美女结尾
![福利](fl.jpg)
####### image from [zenglinghua329](http://zenglinghua329.tumblr.com/)
