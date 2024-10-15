import scrapy
from lxml import etree


class HuyaVedioSpider(scrapy.Spider):
    name = "huya_vedio"
    allowed_domains = [""]
    start_urls = ["https://www.huya.com/video/g/all?set_id=0&order=hot&page=1"]
    cookies_html = {
        'huya_ua': 'webh5&0.0.1&activity',
        '__yamid_new': 'CAC1E1D9AF3000011B48EC6010501D9C',
        'game_did': 'S7FLnlu2RMjdzA43EEZqSMN703887e1FvBq',
        'udb_guiddata': '253de470ab4c4327996091ff7d7fc313',
        'guid': '0a7daacc864e5366f6016fbe70be1038',
        'udb_deviceid': 'w_847247826520498176',
        '__yamid_tt1': '0.1443027931016705',
        'sdidshorttest': 'test',
        'alphaValue': '0.80',
        'SoundValue': '0.53',
        'isInLiveRoom': '',
        'sdid': '0UnHUgv0_qmfD4KAKlwzhqShi8v769LJXgkzP-nDw4C1FJ1gLOjF-ny5z9eO-7Brqqk7XQtTdpHOjTfeL-00bZgFIa1H_MuPP0i77E0tax1TWVkn9LtfFJw_Qo4kgKr8OZHDqNnuwg612sGyflFn1duJhZJgkHgi7S5LddP-G_N8WLAO0mqQKDk78V8e52ejr',
        'sdidtest': '0UnHUgv0_qmfD4KAKlwzhqShi8v769LJXgkzP-nDw4C1FJ1gLOjF-ny5z9eO-7Brqqk7XQtTdpHOjTfeL-00bZgFIa1H_MuPP0i77E0tax1TWVkn9LtfFJw_Qo4kgKr8OZHDqNnuwg612sGyflFn1duJhZJgkHgi7S5LddP-G_N8WLAO0mqQKDk78V8e52ejr',
        'hiido_ui': '0.8190485876759654',
        'Hm_lvt_51700b6c722f5bb4cf39906a596ea41f': '1722221968,1722520344,1722521163',
        'HMACCOUNT': 'DFE92F4D78B4A9FD',
        'udb_passdata': '3',
        '__yasmid': '0.1443027931016705',
        '_yasids': '__rootsid%3DCAD76F5FC950000173931340182013F6',
        'Hm_lvt_9fb71726843792b1cba806176cecfe38': '1722520491,1722521215',
        'amkit3-player-danmu-pop': '1',
        'amkit3-v-player-session-id': '0.7620111277869659',
        'amkit3-v-player-machine-id': '0.8556698721651097',
        'amkit3-v-player-profile-volume': '0.5',
        'Hm_lpvt_9fb71726843792b1cba806176cecfe38': '1722522893',
        'Hm_lpvt_51700b6c722f5bb4cf39906a596ea41f': '1722523241',
        'rep_cnt': '122',
    }
    headers_html = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.huya.com/video/g/all?',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    def start_requests(self):
        yield scrapy.Request(
            url = self.start_urls[0],
            headers=self.headers_html,
            cookies=self.cookies_html,
            callback=self.get_lei

        )

    def get_lei(self, response):
        url = 'https://www.huya.com/video/g/all?set_id={}&order=hot&page={}'
        want_lei = input('请输入想要的类型')
        response = response.text
        A = etree.HTML(response)
        lei_dic = {}
        lei_id_list = A.xpath('//div[@class="vhy-list-category-list"]/a/@href')
        lei_list = A.xpath('//div[@class="vhy-list-category-list"]/a/text()')
        for lei, lei_id in zip(lei_list, lei_id_list):
            lei_dic[f'{lei}'] = lei_id
        if want_lei in lei_dic.keys():
            set_id = lei_dic[f'{want_lei}']
            set_id = set_id.split('set_id=')[1]
            for i in range(1, 51):
                 yield scrapy.Request(
                    url=url.format(set_id, i),
                    headers=self.headers_html,
                    cookies=self.cookies_html,
                    callback=self.parse,
                    dont_filter=True
                )
        else:
            print('没有该类型')

    def parse(self, response):
        url = 'https://liveapi.huya.com/moment/getMomentContent?videoId={}'
        response = response.text
        A = etree.HTML(response)
        data_list = A.xpath('//ul[@class="vhy-video-list clearfix "]/li')
        for data in data_list:
            vid = data.xpath('./a/@href')[0].split('/')[-1].split('.')[0]
            name = data.xpath('./a/@title')[0]
            yield scrapy.Request(
                url=url.format(vid),
                headers=self.headers_html,
                cookies=self.cookies_html,
                meta={'name': name},
                callback=self.get_vedio_link,
                dont_filter=True
            )

    def get_vedio_link(self, response):
        response = response.json()
        link = response['data']['moment']['videoInfo']['definitions'][0]['url']
        name = response['data']['moment']['title']
        yield scrapy.Request(
            url=link,
            headers=self.headers_html,
            cookies=self.cookies_html,
            meta={'name': name},
            callback=self.get_data,
            dont_filter=True

        )

    def get_data(self, response):
        name = response.meta['name']
        data = response.body
        item = {
            'data': [name, data]
        }
        yield item
