import scrapy
from scrapy import Request, Spider, FormRequest
import nest_asyncio
import asyncio
from playwright import async_playwright
from pyquery import PyQuery as pq

nest_asyncio.apply()


class SnailSpider(scrapy.Spider):
    name = 'snail'
    allowed_domains = ['www.chinabond.com.cn']
    start_urls = ['https://www.chinabond.com.cn/jsp/include/CB_CN/issue/issuemiddleinclude.jsp']
    domain = 'https://www.chinabond.com.cn'
    url = 'https://www.chinabond.com.cn/jsp/include/CB_CN/issue/issuemiddleinclude.jsp'
    data = {
        "form_bondtype": "21770",
        "form_bondtype1": "21770",
        "form_cxpj": "ROOT>业务操作>发行与付息兑付>债券种类>国债",
        "form_zzlx": "国债",
        "form_is_encoder": "true",
        "form_keyword": "",
        "xxlx": "fxwj",
        "_tp_fxwj": ""
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        'Referer': 'https://www.chinabond.com.cn/Channel/21000',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url,
            formdata=self.data,
            callback=self.parse_index,
            headers=self.headers,
            dont_filter=True
        )

    def parse_index(self, response):
        html = response.text
        doc = pq(html)
        list_fxwj = doc('#list_fxwj li').items()
        content = [(i.find('a').attr("title"), i.find('a').attr("href"), i.children()[0].text,) for i in list_fxwj]

        # 详情页
        for i in content:
            yield Request(
                self.domain + i[1],
                callback=self.parse_detail,
            )

        # 翻页
        self.data['_tp_fxwj'] = self.data['_tp_fxwj'] if self.data['_tp_fxwj'] else '0'
        if self.data['_tp_fxwj'] != '2':
            self.data['_tp_fxwj'] = str(int(self.data['_tp_fxwj']) + 1)
            yield scrapy.FormRequest(
                url=self.url,
                formdata=self.data,
                callback=self.parse_index,
                headers=self.headers,
                dont_filter=True
            )

    def parse_detail(self, response):
        # 解析详情页，输出详情页截图
        # TODO 设置并发大小
        html = pq(response.text)
        title = html.find('.zw_main2 strong')
        print(f'now page title is {title.text()}')

        async def playweight_demo():
            async with async_playwright() as p:
                width, height = 1366, 768
                browser = await p.chromium.launch(headless=True, devtools=True, args=['--disable-infobars',
                                                                                      f'--window-size={width},{height}'])
                page = await browser.newPage()
                await page.setExtraHTTPHeaders(headers=self.headers)
                await page.setViewportSize(width, height)
                await page.goto(response.url)
                await page.pdf()
                await page.screenshot(path=f'/Users/wenyin/Desktop/work/practice/spider_chinabond/bondspider/static/{str(title.text())}.png')
                await browser.close()

        asyncio.get_event_loop().run_until_complete(playweight_demo())


if __name__ == '__main__':
    pass
