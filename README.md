# StableDiffusionTelegramBot
通过长轮询监听telegram的api获取消息，解析消息后调用StableDiffusion的api绘图。目前支持文生图。

打包版下载地址 https://wwi.lanzoup.com/b0fgy69gh
密码:40ld

注册tg机器人和获取chatId可以参考这个链接 https://hellodk.cn/post/743。
获取你的机器人token

使用方式  

一、把这两个文件（tg绘图.py和config.txt）放在同一个文件夹中  

二、在config.txt填入你的机器人token  

三、（可选）修改其他默认参数，建议加入白名单（chatId），例如"CHAT_ID = -123456789, -321654987,"  

四、开启StableDiffusion的api功能

五、启动脚本

六、在tg中发送/ht +你的绘图参数。例如：/ht (eyewear_on_head: 1.2), (rating:safe: 1.2), (1girl: 1.2), (sunglasses: 1.2), (purple_hair), (gloves), (solo), jacket, holding, purple_eyes, blurry, breasts, phone, shirt, belt, cellphone, upper_body, blurry_background, bangs, sidelocks, white_shirt, long_hair, long_sleeves, looking_at_viewer, smartphone, closed_mouth, red_gloves, expressionless, hair_between_eyes, black_jacket, jacket_on_shoulders,Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 7.0, Seed: 613188881, Size: 512x768, Enable_hr:True,ntags: paintings, sketches, (worst quality:2),(low quality:2), (extra fingers:2), (extra toes:2),bad-picture-chill-75v, badhandv4, easynegative, negative_hand-neg, ng_deepnegative_v1_75t

![image](https://github.com/1803233552/StableDiffusionTelegramBot/assets/71918224/7dc3467a-4d09-4704-8e5d-b424b8f5ac05)


对机器人打出'/help'，获取默认例子提示

![image](https://github.com/1803233552/StableDiffusionTelegramBot/assets/71918224/0cdee482-3c5c-4696-8c37-40b665803d9d)


参数后面接':'，例如'Steps: 28'。目前可修改参数Steps（步数）、Sampler（采样方式）、CFG scale（相关性）、Seed（种子）、Size（图片大小）、Enable_hr（为true开启超分辨率，同时支持中文“高清：开”）、ntags（负面词）。可以中英文符号混用。

请注意ntags要放在最后。不使用这些参数也能正常绘图。

偶尔会报错远程主机关闭了链接，这个不用管
