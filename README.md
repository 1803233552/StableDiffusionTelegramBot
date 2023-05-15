# StableDiffusionTelegramBot
通过telegram调用StableDiffusion绘图

注册tg机器人可以参考这个链接 https://hellodk.cn/post/743。
获取你的机器人token

使用方式  

一、把这两个文件放在同一个文件夹中  

二、在config.txt填入你的机器人token  

三、（可选）修改其他默认参数，建议加入白名单（chatId），例如"CHAT_ID = -123456789, -321654987,"  

四、开启StableDiffusion的api功能  

五、在tg中发送/ht +你的绘图参数。例如：/ht (eyewear_on_head: 1.2), (rating:safe: 1.2), (1girl: 1.2), (sunglasses: 1.2), (purple_hair), (gloves), (solo), jacket, holding, purple_eyes, blurry, breasts, phone, shirt, belt, cellphone, upper_body, blurry_background, bangs, sidelocks, white_shirt, long_hair, long_sleeves, looking_at_viewer, smartphone, closed_mouth, red_gloves, expressionless, hair_between_eyes, black_jacket, jacket_on_shoulders,Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 7.0, Seed: 613188881, Size: 512x768, Enable_hr:True,ntags: paintings, sketches, (worst quality:2),(low quality:2), (extra fingers:2), (extra toes:2),bad-picture-chill-75v, badhandv4, easynegative, negative_hand-neg, ng_deepnegative_v1_75t

目前可修改参数Steps（步数）、Sampler（采样方式）、CFG scale（相关性）、Seed（种子）、Size（图片大小）、Enable_hr（为true开启超分辨率）、ntags（负面词）。
请注意ntags要放在最后。不使用参数也能运行。
