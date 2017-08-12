# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from autohome.items import KoubeiItem, KoubeiFailedItem
from selenium import webdriver
from autohome.pipelines import KoubeiPipeline

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import math

def chunk(L, num):
    length = len(L)
    if length <= num:
        return L
    l = math.ceil(length/num)
    result = []
    for i in range(num):
        result.append( L[ i*l : (i+1)*l ] )
    return result


class KoubeiSpider(scrapy.Spider):
    name = "koubei"
    allowed_domains = ["k.autohome.com.cn"]
    pipeline = set([KoubeiPipeline, ])
    # start_urls = ['http://k.autohome.com.cn/']
    base_url = 'http://k.autohome.com.cn'

    def __init__(self, seq=None, *args, **kwargs):
        super(KoubeiSpider, self).__init__(*args, **kwargs)
        self.seq = int(seq)
        self.browser = webdriver.Chrome()
        self.browser.set_page_load_timeout(15)

    def __del__(self):
        self.browser.quit()

    def start_requests(self):
        all_series = [3895,2097,179,401,923,822,385,386,2275,3891,266,884,2846,582,2745,3170,692,18,2951,812,19,509,650,370,471,538,472,740,146,2264,593,412,511,2730,2734,2736,2738,2739,2841,148,2740,2735,2737,2994,2447,2575,2446,2444,4077,3774,3677,3343,2236,3412,155,3941,66,65,2561,373,3230,3726,3302,317,2963,2968,202,2847,270,153,2388,2387,675,271,3053,159,587,161,3357,2196,3189,2726,2727,2728,2729,2725,3913,2073,168,172,415,2838,703,4175,162,3800,623,2852,2252,3714,3661,4137,3874,3997,3284,3361,4158,3426,3794,3557,2791,2787,3673,3839,3928,3795,3417,3427,4154,2482,3231,3191,3916,4061,4009,3428,2943,3712,3884,3533,4015,3537,3035,2126,966,2915,622,2960,965,3221,2959,852,588,197,3248,3862,2562,3823,2564,2084,2034,2005,52,398,2966,365,56,450,3079,3683,3688,60,469,3278,267,237,59,192,235,683,595,467,57,300,3451,2842,2967,2719,2717,2718,3264,3704,3901,2723,2721,2720,2197,2833,2722,914,3665,3695,632,466,2310,3000,2565,314,3582,3859,3104,4179,859,135,4102,880,3460,81,3876,2168,3085,78,694,449,723,897,900,231,233,4173,4073,831,579,407,927,3283,2091,2085,798,2088,3059,2761,2944,3780,2806,3430,3781,940,540,997,489,417,4167,3234,2619,3068,877,3632,987,2299,437,688,99,724,689,2472,2047,184,640,277,185,186,2896,3554,166,164,834,875,3751,982,525,344,592,3014,901,305,2685,306,390,3922,3980,2478,4141,4142,3640,3058,76,3217,2045,3924,2778,3204,2119,2785,2429,2567,2788,3422,484,2046,1008,520,705,590,4181,3311,4182,3893,3155,2600,2605,3526,3514,3685,2505,2954,2566,3783,2504,2604,3227,4011,4012,4013,2923,3091,2606,2459,2090,2120,2462,3101,2122,535,2001,2304,2200,491,536,2653,493,624,6,552,492,3506,3507,3504,3505,3508,3963,2952,3309,3324,898,2078,2314,545,145,4045,3197,3103,614,3457,528,2922,333,874,826,144,149,207,633,871,3964,16,496,442,905,15,360,368,557,700,430,780,372,224,210,3416,631,669,82,3999,86,539,574,2198,576,602,575,3716,3166,2901,560,2839,3279,2512,2510,951,561,562,3984,3637,3829,3828,3925,4023,3086,3830,3463,3493,2556,3786,3341,3119,1006,3461,790,2990,3792,3789,3970,554,3301,3414,3128,3785,2540,2742,3698,3699,3036,3502,2865,2452,2497,2500,2501,3697,2499,2490,2491,2494,2495,2744,2498,4086,606,2769,2776,2530,3634,126,2477,676,2682,4027,3016,3720,361,889,308,459,367,359,2261,2767,3267,465,89,90,91,542,601,2262,544,543,3126,771,110,3462,2237,505,770,109,882,526,2527,45,46,371,375,111,170,513,3851,2607,983,2107,2574,206,549,964,2244,963,550,334,107,2354,762,2454,2453,3633,2455,2475,2895,3754,2894,3877,3346,364,3347,659,3693,117,3615,2871,2863,3175,498,577,3518,2523,4192,3814,2524,2025,97,102,704,2302,2353,378,713,684,2024,3440,4035,2535,3991,3990,3676,3821,2542,3089,2579,3307,3735,2577,661,980,2355,955,947,2974,3662,2093,2095,2094,3069,3524,2141,3349,3782,3691,2560,3574,4094,967,968,3272,2774,2599,2571,2568,3480,3477,3134,2488,2885,3159,3139,3140,2114,2306,969,865,1015,864,2487,2485,2486,3840,392,3038,67,2536,481,68,3454,2615,2027,2123,3481,3074,2124,3298,395,4131,2572,3243,3636,3638,3235,3149,2673,470,4205,2766,3075,3994,823,844,824,47,527,696,3163,3162,2941,3006,3214,855,3160,2481,2318,4130,38,379,2754,2755,2973,3108,2771,428,556,3911,3844,570,461,507,194,460,856,862,3607,2144,2133,3803,3896,477,290,2108,4065,4066,2517,2515,3455,3846,2160,4162,2211,2516,2212,673,291,23,3872,4072,521,121,504,3062,777,263,503,3048,3589,3788,3556,4139,3465,2051,3467,801,989,447,608,132,841,474,4133,409,133,2155,2192,2840,2111,2964,2156,609,799,138,421,611,616,3407,3408,2956,3395,3961,3443,3444,3490,2541,3351,4090,2543,3545,3080,2752,2581,3546,2569,828,3456,567,816,572,660,617,2674,2514,2860,3981,3466,3639,3681,4149,4083,3209,2903,3312,589,178,456,258,328,2537,2545,2810,2402,3955,2601,2711,2712,2837,3763,3721,3722,3136,2659,4076,2660,2665,3853,3868,2325,3898,2986,2985,3549,3885,3886,2976,3320,3628,2573,2576,3194,2582,911,2610,2611,3656,3655,3360,4172,3511,4039,3854,3384,2496,2493,2484,3156,2476,3017,2489,2492,517,3207,3802,3989,2949,488,970,2629,311,49,462,426,3586,3581,3971,3983,3835,3836,4161,4160,2068,731,732,566,487,227,2207,342,380,222,3864,2277,3277,354,174,727,2102,2103,836,265,3015,3838,3559,2063,403,261,112,201,341,352,3442,3758,3934,351,332,3238,697,3870,199,908,2268,686,196,2765,2184,188,257,2248,2503,2800,3631,3082,2957,596,2312,3326,3228,3229,3220,2134,3987,2502,597,443,3083,583,691,928,2125,706,3124,2521,961,3472,569,3034,3150,2520,962,815,568,2991,869,794,758,793,95,103,75,3216,2534,3112,2049,432,872,3185,3528,529,2242,3858,362,94,500,508,892,2176,3436,3438,3439,2883,3413,833,571,468,501,635,3871,3521,4191,802,3565,69,754,850,256,72,3177,77,272,681,891,555,2147,532,835,3065,3547,531,533,209,749,750,904,2241,930,3178,3179,3181,3182,3180,3294,2418,2987,433,641,363,3154,22,2118,3968,3066,655,3096,584,2391,1005,672,578,304,658,295,322,3060,903,551,2428,289,191,389,4040,3809,3767,3620,3382,3733,2902,2293,3491,3153,2835,3736,3152,2836,3151,2296,3040,2295,2988,3939,3293,3432,4096,2642,524,888,2748,3328,806,464,479,2021,381,348,653,670,182,2563,2263,4099,3157,3405,2980,4223,3300,2914,837,2953,2324,2989,3397,3195,3766,83,451,84,518,530,434,87,478,612,854,85,996,2178,2180,2331,396,3648,3920,4115,2955,2341,3475,2867,3226,3618,3904,813,2319,2886,3385,3286,2246,3664,3954,413,565,876,2137,284,142,454,298,452,591,453,3448,1010,890,2681,502,1016,281,275,3820,3817,522,2381,2086,656,425,634,3957,564,448,64,475,63,355,53,2466,2113,2853,2578,438,958,208,702,436,264,204,205,376,316,2062,3857,537,482,2743,2779,3978,3977,4080,2297,2970,2972,2109,797,791,804,853,1004,2958,620,343,211,3487,3486,25,24,3131,668,458,483,873,128,2768,4147,3008,377,1018,369,486,580,2332,325,651,2570,3244,3064,2608,3192,599,13,345,506,455,3406,2214,3132,516,3372,485,141,139,2751,286,287,285,2557,2417,283,414,3847,3848,3849,3013,382,519,3171,3290,2962,772,357,858,356,3269,4151,3389,3390,3391,3392,3393,2357,2664,2805,2538,2539,909,613,725,959,3969,3653,3306,3882,463,693,3420,3158,3411,404,175,3861,2678,2190,585,177,494,406,981,2506,2139,2451,3657,2855,3570,2456,3946,3562,3935,3576,4198,2834,718,2105,714,3292,1007,2764,3959,3073,2927,2115,3415,3672,358,51,586,4107,814,690,866,2649,50,431,429,3613,2117,2256,3164,3453,756,2984,1017,975,127,255,446,131,252,594,457,510,3703,3702,3090,2348,3335,657,2583,4105,3923,2313,4031,163,397,420,439,678,546,808,682,3873,98,639,3429,2945,792,4043,232,293,388,230,476,473,329,480,2473,212,440,2440,3906,2378,2445,2888,939,3979,3081,879,2716,101,878,2781,106,444,104,2526,2525,2465,2469,2468,3775,3776,3052,3459,913,3824,2131,2464,2870,2603,2533,2532,2531,3553,3591,605,3535,2992,3201,3097,3098,3043,3099,3100,122,383,2400,581,3202,416,3087,424,2828,3777,2228,3237,3706,3827,3497,2999,2770,2857,2998,2323,3530,2294,3289,411,860,523,825,490,130,2658,3644,2850,627,2143,4178,3215,2519,3881,2522,2613,2081,4070,3793,4038,2230,3575,3779,3529,708,3899,2336,2334,2480,3002,2337,3425,3627,558,663,2161,2171]
        # random.shuffle()
        random.seed('koubei')
        random.shuffle(all_series)
        all_series = chunk(all_series,8)

        #此处手动启动8次，8个浏览器同时工作
        series = all_series[self.seq]

        # series = [496]
        urls = []
        for series_id in series:
            url1 = "http://k.autohome.com.cn/%s/"%series_id
            url2 = "http://k.autohome.com.cn/%s/stopselling/"%series_id
            urls.append(url1)
            urls.append(url2)
        # urls = [
        #     # 'http://k.autohome.com.cn/135/',
        #     #待附加口碑
        #     # 'http://k.autohome.com.cn/spec/26931/view_1443546_1.html?st=3&piap=0|496|0|0|1|0|0|0|0|0|1',
        #     # 'http://k.autohome.com.cn/spec/28541/view_1425021_1.html?st=1&piap=0|135|0|0|1|0|0|0|0|0|1',
        #     # 'http://k.autohome.com.cn/496/',
        #     'http://k.autohome.com.cn/496/stopselling/',
        # ]
        for url in urls:
            # yield scrapy.Request(url=url, callback=self.koubeiUrlParse)
            # yield scrapy.Request(url=url, callback=self.koubeiParse)
            yield scrapy.Request(url=url, callback=self.koubeiListUrlParse)

    #从车系口碑页 获取列表页url
    def koubeiListUrlParse(self, response):
        #自身是第一页
        yield scrapy.Request(url=response.url, callback=self.koubeiUrlParse)

        soup = BeautifulSoup(response.text, 'lxml')
        #未必有口碑且多页
        page_last = soup.find('a', class_='page-item-last')
        if not page_last:
            return

        url_extend = page_last.attrs['href']
        if url_extend.find('index_')<0:
            return
        page_number = int(url_extend[url_extend.find('index_')+6:-5])
        #页面从2开始到最后
        for num in range(page_number-1):
            num = str(num + 2)
            url = self.base_url + url_extend[0:url_extend.find('index_')+6] + num + url_extend[url_extend.find('.'):]
            print("发现链接：%s"%(url))
            yield scrapy.Request(url=url, callback=self.koubeiUrlParse)

    #获取详情页url
    def koubeiUrlParse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        titles = soup.findAll('div', class_='cont-title fn-clear')
        for title in titles:
            url = title.find('a').attrs['href']
            yield scrapy.Request(url=url, callback=self.koubeiParse)

    def koubeiParse(self, response):
        try:
            yield self.koubeiHtml(response)
        except Exception:
            item = KoubeiFailedItem()
            item['url'] = response.url
            print("url爬去异常：", response.url)
            yield item
        return


    def koubeiHtml(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        # 口碑左侧信息
        mouthcon_cont_left = soup.find('div', class_='mouthcon-cont-left')
        item = KoubeiItem()
        item['url'] = response.url

        for dl_s in mouthcon_cont_left.findAll('dl'):
            item_name = dl_s.find('dt').get_text(strip=True)
            item_value = dl_s.find('dd').get_text(strip=True)
            if item_name=='购买车型':
                item['series_id'] = dl_s.findAll('a')[0].attrs['href'][1:]
                item['series_name'] = dl_s.findAll('a')[0].get_text(strip=True)
                item['spec_id'] = dl_s.findAll('a')[1].attrs['href'][6:]
            if item.switcher.get(item_name):
                item[item.switcher.get(item_name)] = item_value

        ##有可能多个内容
        mouthcons = soup.findAll('div', class_='mouth-item')
        for mouthcon in mouthcons:
            type = mouthcon.find('i', class_='icon icon-zj').get_text()
            if type == '口碑':
                koubei_content = mouthcon

        # 口碑主要内容信息
        item['date'] = koubei_content.find('div', class_='title-name name-width-01').find('b').get_text(strip=True)
        item['title'] = koubei_content.find('div', class_='kou-tit').find('h3').get_text(strip=True).lstrip("《").rstrip(
            '》')

        # 正文内容
        text_con = koubei_content.find('div', class_='text-con')
        replace_content_s_list = text_con.findAll('span')

        # 启动浏览器
        self.browser.get(response.url)

        # 等待完成
        first_class = replace_content_s_list[0].attrs['class'][0]
        element_present = EC.presence_of_element_located((By.CLASS_NAME, first_class))

        WebDriverWait(self.browser, 2).until(element_present)

        # 字典，存储获取过的内容
        span_class_dict = {}
        for replace_span_s in replace_content_s_list:
            cls = replace_span_s.attrs['class'][0]
            if cls not in span_class_dict:
                script = "return window.getComputedStyle(document.getElementsByClassName('%s')[0],'before').getPropertyValue('content')" % (
                cls)
                trans = self.browser.execute_script(script).strip('\"')
                span_class_dict[cls] = trans
            replace_span_s.replace_with(span_class_dict[cls])

        # 清除style和script
        [i.extract() for i in koubei_content.findAll('style')]
        [i.extract() for i in koubei_content.findAll('script')]

        item['content'] = koubei_content.get_text(strip=True)
        print("爬去成功：",item['title'],item['url'])
        # self.browser.quit()
        return item

