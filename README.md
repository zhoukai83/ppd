# ppd
2017-2018年的时候发现拍拍贷还不错，其中散标中的自负坏账的信用标利率高，刚开始B级好像能达到20-24%左右，试验了一段时间发现收益能覆盖坏账，就打算投了。

然后呢，拍拍贷的标，会提供每个借贷标的的各个维度的详细信息，包括借款人年龄，性别，文化程度，还款来源，毕业院校，月收入情况，负债情况，还款情况等...

开始的时候，信用标还很容易投，所以我就利用学过的机器学习的技术，先把历史标的的信息爬取下来，然后进行数据清洗，分析，接着预测每个标的是不是会成为坏账，来辅助投标

后来，可能大家都发现了信用标收益不错，一个信用标出来，1分钟内就被抢了，所以就写了段代码，利用Selenium来做webUI自动化分析投标

再后来，一个信用标不到5秒就抢光了，就改进，放弃Selenium, 而是通过分析UI的http请求，发送http请求来获取标的信息，投标，期间将请求进化成异步方式

再后来，为了优先抢到好的信用标，又改进成用拍拍贷官方提供的SDK API来获取标的信息，分析，投标

再后来，竞争越来越激烈，一个标的出来不到0.1-0.5秒就抢光了，就改进成多客户端获取标的信息，部署到几个不同的地区

最后，变成了盲抢标模式，只要发现有标的就盲投

直到2019年拍拍贷退出，依靠这段程序获得了还不错的收益。

