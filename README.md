# StableDiffusionTelegramBot
通过长轮询监听telegram的api获取消息，解析消息后调用StableDiffusion的api绘图。目前支持文生图。

打包版下载地址 https://wwi.lanzoup.com/b0fgy69gh
密码:40ld

注册tg机器人，获取你的机器人token和获取chatId可以参考这个链接 https://hellodk.cn/post/743。

一些参数配置可以参考这个 https://www.dengnz.com/2020/11/23/telegram-%e6%9c%ba%e5%99%a8%e4%ba%ba%e7%9a%84%e7%94%b3%e8%af%b7%e5%92%8c%e8%ae%be%e7%bd%ae%e5%9b%be%e6%96%87%e6%95%99%e7%a8%8b/

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

tg交流群：https://t.me/+X2u2e-OTlzczZmQ1


English

By using long polling to listen to the Telegram API for messages, the script parses the messages and calls the StableDiffusion API to generate graphs. Currently, it supports generating charts for the biological sequence.

Download link for the packaged version: https://wwi.lanzoup.com/b0fgy69gh Password: 40ld

To register a Telegram bot and obtain your bot token and chat ID, you can refer to this link: https://hellodk.cn/post/743.

For configuring some parameters, you can refer to this link: https://www.dengnz.com/2020/11/23/telegram-%e6%9c%ba%e5%99%a8%e4%ba%ba%e7%9a%84%e7%94%b3%e8%af%b7%e5%92%8c%e8%ae%be%e7%bd%ae%e5%9b%be%e6%96%87%e6%95%99%e7%a8%8b/

Usage:

1.Place the two files (tg绘图.py and config.txt) in the same folder.

2.Fill in your bot token in the config.txt file.

3.(Optional) Modify other default parameters. It is recommended to include your chat ID in the whitelist (e.g., "CHAT_ID = -123456789, -321654987,").

4.Enable the API feature in StableDiffusion.

5.Start the script.

6.In Telegram, send the command /ht followed by your graph parameters. For example: /ht (eyewear_on_head: 1.2), (rating:safe: 1.2), (1girl: 1.2), (sunglasses: 1.2), (purple_hair), (gloves), (solo), jacket, holding, purple_eyes, blurry, breasts, phone, shirt, belt, cellphone, upper_body, blurry_background, bangs, sidelocks, white_shirt, long_hair, long_sleeves, looking_at_viewer, smartphone, closed_mouth, red_gloves, expressionless, hair_between_eyes, black_jacket, jacket_on_shoulders,Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 7.0, Seed: 613188881, Size: 512x768, Enable_hr:True,ntags: paintings, sketches, (worst quality:2),(low quality:2), (extra fingers:2), (extra toes:2),bad-picture-chill-75v, badhandv4, easynegative, negative_hand-neg, ng_deepnegative_v1_75t

![image](https://github.com/1803233552/StableDiffusionTelegramBot/assets/71918224/7dc3467a-4d09-4704-8e5d-b424b8f5ac05)


Send '/help' to the bot and get the default example prompts.

![image](https://github.com/1803233552/StableDiffusionTelegramBot/assets/71918224/0cdee482-3c5c-4696-8c37-40b665803d9d)


Parameters followed by ':' are translated as follows, for example, 'Steps: 28'. The current parameters that can be modified are: Steps (number of steps), Sampler (sampling method), CFG scale (correlation), Seed (random seed), Size (image size), Enable_hr (set to true to enable high resolution, also supports Chinese '高清：开'), and ntags (negative words). Both Chinese and English symbols can be used interchangeably.

Please note that ntags should be placed at the end. It is also possible to generate graphs without using these parameters.

Occasionally, there may be an error stating that the remote host has closed the connection. You can ignore this.

Telegram group：https://t.me/+X2u2e-OTlzczZmQ1
