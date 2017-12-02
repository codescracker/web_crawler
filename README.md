This project is a web crawler based on Scrapy framework which allow the program leverage the power of async I/O and speed up the data collections efficiency. The data collected by the project is used for analytics purpose.

The project includes 3 important components: spider, item, pipeline:
1. Spider is responsible for handle request and response in async way.
2. Item is responsible for transform the shape of data and guranteen the quality of data.
3. Pipeline is used to handle the loading of data. It dispatches the data storage mechanism for both file system and database solution.

The project contains 4 spiders which is used to crawler data from target websites:
1. Zhihu Spider: this spider is used to crawl questions and answers from zhihu.com(Chinese version of Quara)
2. Jobble Spider: this spider is used to crawl IT articles from jobbole.com.
3. lagou Spider: this spider is used to crawl job data fom lagou.com(Chinese version of indeed.com).
4. Carfax Spider: this spider is used to crawl used car information from carfax.com.

The data storage solution for this project is MySQL. The Database is hosted on AWS RDS. 

The project is deployed on AWS lightsail instance.
 
To avoid being blocked by target websites, there are 3 adjustments: 
1. Customize download middleware of Scrapy framework and make it be capable for generating ramdom header for each request.
2. Customize download middleware of Scrapy framework which send each request with help of proxy server. Build a script which update proxy ip pool constantly.
3. Ban cookie for spiders which do not require log in.

To parse dynamic webpage, Selenium Webdriver and PhantomJS are integrated into particular steps of scrapy, although it comes with promise of performance(webdriver is not asysc).



