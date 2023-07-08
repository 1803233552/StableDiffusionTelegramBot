import os
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import re
import urllib.parse
import time as tm
import csv
import random

# 声明全局变量
global TOKEN
global CHAT_ID
global localurl
global temp_dir
global loraPath
global loraFilename
global max_filename_length
global defaultSteps
global defaultNegative_prompt
global defaultSeed
global defaultSampler_index
global defaultCfg_scale
global defaultSize
global defaultEnable_hr
global defaultHr_scale
global defaultHr_resize_x
global defaultHr_resize_y
global defaultHr_upscaler
global defaultHr_second_pass_steps
global defaultDenoising_strength

# lora相关
loraData = {}  # 用于存储编号和值的字典
global loraData_dict

modified_filenames = []

# lora列表页数
global total_pages
global pages
global last_text_to_print


# 1.0.8,支持群聊话题，修复lora列表读取
# 正常使用,保存信息，自动识别聊天对象发送，可读取自定义参数,可以读取webui的输出参数
# 正面词会固定增加逗号，如果原图没有逗号会产生误差bug）

# 读取配置文件
def read_config(filename):
    config = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
                config[key] = value
    return config


# 加载配置文件
def load_config():
    # 声明全局变量
    global TOKEN
    global CHAT_ID
    global localurl
    global temp_dir
    global loraPath
    global loraFilename
    global max_filename_length
    global defaultSteps
    global defaultNegative_prompt
    global defaultSeed
    global defaultSampler_index
    global defaultCfg_scale
    global defaultSize
    global defaultEnable_hr
    global defaultHr_scale
    global defaultHr_resize_x
    global defaultHr_resize_y
    global defaultHr_upscaler
    global defaultHr_second_pass_steps
    global defaultDenoising_strength

    # 读取配置文件
    config = read_config('config.txt')

    print(f"读取默认参数")

    # 读取 telegram token
    TOKEN = config.get('TOKEN')
    if len(TOKEN) == 0:
        print(f"TOKEN为空，请检查config.txt文件")
    # print(TOKEN)

    # 读取白名单 id
    CHAT_ID = config.get('CHAT_ID', '').split(',')
    if CHAT_ID == ['']:
        CHAT_ID = []
    print(f"白名单:{CHAT_ID}")

    # 读取本地sd地址
    localurl = config.get('localurl', 'http://127.0.0.1:7860')
    print(f"本地sd地址:{localurl}")

    # 读取保存图片位置
    temp_dir = config.get('temp_dir', './image')
    print(f"保存图片位置:{temp_dir}")

    # 读取lora保存位置
    loraPath = config.get('loraPath', '')
    print(f"lora保存位置:{loraPath}")

    # 读取lora预设保存位置
    loraFilename = config.get('loraFilename', 'loraname_list_tg.csv')
    print(f"lora预设保存位置:{loraFilename}")

    # 读取允许的最大文件名长度
    max_filename_length = int(config.get('max_filename_length', '100'))

    # 读取绘图默认参数
    print(f"绘图默认参数")
    # 步数
    defaultSteps = int(config.get('defaultSteps', '40'))
    print(f"步数:{defaultSteps}")

    # 负面词
    defaultNegative_prompt = config.get('defaultNegative_prompt',
                                        'EasyNegative, badhandv4, negative_hand-neg, ng_deepnegative_v1_75t, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry')
    print(f"负面词:{defaultNegative_prompt}")

    # 种子
    defaultSeed = int(config.get('defaultSeed', '-1'))
    print(f"种子:{defaultSeed}")

    # 采样方式
    defaultSampler_index = config.get('defaultSampler_index', 'DPM++ 2M Karras')
    print(f"采样方式:{defaultSampler_index}")

    # 相关性
    defaultCfg_scale = float(config.get('defaultCfg_scale', '7.0'))
    print(f"相关性:{defaultCfg_scale}")

    # 大小
    defaultSize = config.get('defaultSize', '512x768')
    print(f"图片大小:{defaultSize}")

    # 超分辨率开关
    defaultEnable_hr = config.get('defaultEnable_hr', 'False').lower() == 'true'
    print(f"超分辨率状态:{defaultEnable_hr}")

    # 超分辨率倍数
    defaultHr_scale = int(config.get('defaultHr_scale', '2'))
    print(f"超分辨率倍数:{defaultHr_scale}")

    # 超分辨率宽高
    defaultHr_resize_x = int(config.get('defaultHr_resize_x', '1024'))
    defaultHr_resize_y = int(config.get('defaultHr_resize_y', '1536'))
    print(f"超分辨率宽:{defaultHr_resize_x}")
    print(f"超分辨率高:{defaultHr_resize_y}")

    # 放大算法
    defaultHr_upscaler = config.get('defaultHr_upscaler', 'R-ESRGAN 4x+')
    print(f"放大算法:{defaultHr_upscaler}")

    # 放大采样次数
    defaultHr_second_pass_steps = int(config.get('defaultHr_second_pass_steps', '5'))
    print(f"放大采样次数:{defaultHr_second_pass_steps}")

    # 重绘幅度
    defaultDenoising_strength = float(config.get('defaultDenoising_strength', '0.4'))
    print(f"重绘幅度:{defaultDenoising_strength}")


# 将中文标点转换为英文标点
def convert_chinese_punctuation_to_english(text):
    # 定义中文标点和对应的英文标点
    chinese_punctuation = '，。！？；：“”‘’（）【】『』—…《》〈〉'
    english_punctuation = ',.!?;:""\'\'()[]\'\'--...<>'

    # 使用字符串的替换功能将中文标点替换为英文标点
    for i in range(len(chinese_punctuation)):
        text = text.replace(chinese_punctuation[i], english_punctuation[i])

    return text


# 检测文本是否不为空且最后一个字符不是逗号，并在需要时添加逗号
def add_comma(text):
    if text and text[-1] != ',':
        text += ','
    return text


# 检测结尾是否有逗号或者空格，没有则加上逗号
def add_comma_if_needed(string):
    if string.endswith(',') or string.endswith(' ') or string.endswith('，'):
        return string
    else:
        return string + ','


# 判断字符串中是否包含指定字符串（例如"Steps:"），并检查该字符串之前是否有逗号或空格，如果没有，则在其之前添加逗号
def add_comma_before_keyword(string, keyword):
    if keyword in string:
        index = string.index(keyword)
        if index > 0 and not string[index - 1] in [',', ' ']:
            string = string[:index] + ' ' + string[index:]
    return string


def re_loraname(filename, prefix, suffix):
    if '.safetensors' in filename:
        newname = filename.replace('.safetensors', '')
        modified_filename = prefix + newname + suffix
        modified_filenames.append(modified_filename)
    elif '.pt' in filename:
        newname = filename.replace('.pt', '')
        modified_filename = prefix + newname + suffix
        modified_filenames.append(modified_filename)


# 读取文件
def get_filelist(path):
    prefix = '<lora:'
    suffix = ':1>'
    Filelist = []
    for home, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(home, filename)
            Filelist.append(file_path)
            re_loraname(filename, prefix, suffix)
    return modified_filenames


# 读取文件夹创建缓存
def read_lora(loraPath, loraFilename):
    Filelist = get_filelist(loraPath)
    # print(len(Filelist))
    # for file in Filelist:
    #   print(file)
    existing_data = []
    # 检查是否存在旧的CSV文件
    if os.path.exists(loraFilename):
        # 如果存在，读取旧的文件名列表

        with open(loraFilename, 'r', encoding='utf-16') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    existing_data.append(row[0].split('\t')[0])  # 只取第一列的数据
        # print(f"当前existing_data:{existing_data}")
        # 检查是否有新数据
        new_data = list(set(Filelist) - set(existing_data))

    else:
        # 如果不存在旧的CSV文件，则所有数据都是新数据
        new_data = Filelist


    # 打印提示
    if len(new_data) > 0:
        print(f"有{len(new_data)}个新数据插入")
        # 将新数据追加到CSV文件中
        with open(loraFilename, 'a', encoding='utf-16', newline='') as f:
            writer = csv.writer(f)
            for modified_filename in new_data:
                writer.writerow([modified_filename])
        print(f"当前Lora数量:{len(new_data)}")
    else:
        print("没有新lora数据插入")
        print(f"当前Lora数量:{len(existing_data)}")





# 读取缓存的lora
def load_lora(filename):
    global loraData_dict
    loraData_dict = {}
    with open(filename, 'r', encoding='utf-16') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            key = row[0]
            values = [value for value in row[1:] if value.strip()]
            if values:
                loraData_dict[key] = [key] + values
            else:
                loraData_dict[key] = [key]
    return loraData_dict


# 匹配输入字符串，替换lora
def replace_with_key(string, data_dict):
    print(f"字符串为: {string}")
    words = re.split(r'\s*,\s*', string)  # 根据逗号分割切词
    replaced_words = []
    for word in words:
        replaced_word = word
        # 遍历字典的每一对键值
        for key, value in data_dict.items():
            # 遍历值列表中的每一项
            for item in value[1:]:
                # 构造匹配项的正则表达式模式
                pattern = r'\b' + re.escape(item) + r'\b'
                # 在词语中寻找匹配项
                matches = re.findall(pattern, replaced_word)
                if matches:
                    print(f"在字符串中找到匹配项: {matches}")
                    print(f"匹配到的键值对是: {key}, {item}")
                    # 替换所有匹配项
                    for match in matches:
                        replaced_word = replaced_word.replace(match, key)
        replaced_words.append(replaced_word)
    # 重新拼接替换后的词语
    replaced_string = ', '.join(replaced_words)
    # 返回替换后的字符串
    return replaced_string


# 读取webui格式参数
def changeInfo(info, method):
    # 去除回车符
    info = info.replace("\n", "")
    text = info

    # 获取 Negative prompt 之前的文本
    pattern = r"(.*?)(?=\bNegative prompt:|\bntags:|$)"
    # print("pattern:", pattern)
    match = re.search(pattern, text)

    if match:
        before_negative_prompt = match.group(1).strip()
        # before_negative_prompt = add_comma_if_needed(before_negative_prompt)
        print("Before Negative prompt:", before_negative_prompt)
        # text = re.sub(pattern, "", text)  # 将 Negative prompt 之前的文本 替换为空字符串
    else:
        before_negative_prompt = ""
        # print("Before Negative prompt is empty")

    # 获取 Negative prompt 的值
    pattern = r"Negative prompt:([\s\S]*?)(?=Steps:|$)"
    match = re.search(pattern, text)

    if match:
        negative_prompt = match.group(1).strip()
        print("Negative prompt:", negative_prompt)
        text = re.sub(pattern, "", text)  # 将 negative_prompt 替换为空字符串
    else:
        negative_prompt = ""

    # 获取 Hires upscaler 的值
    pattern = r"Hires upscaler: ([^,]+)"
    match = re.search(pattern, text)
    # print("match:", match)
    # 获取 Hires upscaler 的值
    if match:
        inihires_upscaler = match.group(1).strip() if match.group(1) else defaultHr_upscaler
        print("Hires upscaler:", inihires_upscaler)

        if method == 1:
            # 对参数进行 URL 编码,出现在 URL 中的参数传递部分。在 URL 中，参数值应该进行 URL 编码，以确保特殊字符（如空格、加号等）被正确传递。这里的DPM++ 2M Karras不转码的话会出现错误
            hires_upscaler = inihires_upscaler
            # print("Encoded sampler:", encoded_sampler)
        else:
            hires_upscaler = urllib.parse.quote(inihires_upscaler)

        text = re.sub(pattern, f"Hires upscaler: {hires_upscaler}", text)  # 将 Sampler 替换为新值
    else:
        print("Hires upscaler is empty")

    # 获取 Sampler 的值
    pattern = r"Sampler: ([^,]+)"
    match = re.search(pattern, text)
    # print("match:", match)
    # 获取 Sampler 的值
    if match:
        iniSampler = match.group(1).strip() if match.group(1) else defaultSampler_index
        print("Sampler:", iniSampler)

        if method == 1:
            print(2)
            # 对参数进行 URL 编码,出现在 URL 中的参数传递部分。在 URL 中，参数值应该进行 URL 编码，以确保特殊字符（如空格、加号等）被正确传递。这里的DPM++ 2M Karras不转码的话会出现错误
            sampler = iniSampler
            # print("Encoded sampler:", encoded_sampler)
        else:
            sampler = urllib.parse.quote(iniSampler)

        text = re.sub(pattern, f"Sampler: {sampler}", text)  # 将 Sampler 替换为新值
    else:
        print("Sampler not found")
    # 判断是否需要在 Steps 之前添加逗号
    text = add_comma_before_keyword(text, "Steps:")
    # 这里用ht_text替代了before_negative_prompt
    outInfo = f"{text}, ntags:{negative_prompt}"
    print(f"outInfo:{outInfo}")
    return outInfo


# 加载lora数据
def load_loradata():
    global loraData  # 声明 loradata 为全局变量
    global pages  # 声明 pages 为全局变量
    global total_pages  # 声明 total_pages 为全局变量
    global loraFilename

    loraData.clear()  # 清空字典

    with open(loraFilename, 'r', encoding='utf-16') as file:
        reader = csv.reader(file, delimiter='\t')
        index = 1
        for row in reader:
            values = [value for value in row[1:] if value.strip()]
            if values:
                loraData[index] = [row[0]] + values
            else:
                loraData[index] = [row[0]]
            index += 1

    # 将字典转换为字符串，以便于分页
    result = ''
    for key, value in loraData.items():
        result += f'{key}: {value},\n '

    # 删除最后一个逗号和空格
    result = result[:-2]
    result = result.replace("'", "").replace("[", "").replace("]", "")
    lines = result.split(',\n')  # 按逗号和换行符分割字符串
    pages = [lines[i:i + 50] for i in range(0, len(lines), 50)]  # 将列表按每页99行进行分割


    total_pages = len(pages)  # 总页数


# 查找匹配的lora预设
def match_lora(string):
    global loraData_dict
    result = replace_with_key(string, loraData_dict)
    return result


# 随机lora
def get_random_value(data):
    keys = list(data.keys())
    random_key = random.choice(keys)
    # random_key = keys[1] # 固定位置
    # return data[random_key] # 返回对应键的值
    return random_key  # 返回键的值

def send_message(text, chat_id, message_thread_id, temp_file):
    # 构建发送图片的 API URL
    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'

    # 发送消息
    if message_thread_id is None:
        # 不是话题消息
        if temp_file is None:
            # 发送文本消息
            print("开始发送文本")
            res = requests.post(url=f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={text}")
            print("发送文本完成")
        else:
            # 发送图片消息
            print("开始发送图片")
            res = requests.post(url, data={'chat_id': chat_id, }, files={'photo': open(temp_file, 'rb')})
            print("发送图片完成")
    else:
        # 是话题消息
        if temp_file is None:
            # 发送文本消息
            print("开始发送文本")
            res = requests.post(
                url=f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={text}&reply_to_message_id={message_thread_id}")
            print("发送文本完成")
        else:
            # 发送图片消息
            print("开始发送图片")
            res = requests.post(url, data={'chat_id': chat_id, 'message_thread_id': message_thread_id},
                                files={'photo': open(temp_file, 'rb')})
            print("发送图片完成")

    # 获取消息 ID
    message_id = res.json()['result']['message_id']

    return res


# 绘图
def draw(text_to_print, chat_id, message_thread_id):
    # 开始绘图
    star_text = "开始绘图"
    if message_thread_id is None:
        send_message(star_text, chat_id, message_thread_id=None, temp_file=None)
    else:
        send_message(star_text, chat_id, message_thread_id, temp_file=None)

    # 检查目标文件夹是否存在，如果不存在则创建
    os.makedirs(temp_dir, exist_ok=True)

    # 去除首尾空格
    text_to_print = text_to_print.strip()

    # 将中文标点转换为英文标点
    text_to_print = convert_chinese_punctuation_to_english(text_to_print)

    # 随机tag
    pattern = r"随机"
    match = re.search(pattern, text_to_print)

    if match:
        print("存在 随机")
        # 调用随机函数
        # 随机选择一个值并输出
        random_value = str(get_random_value(loraData_dict))
        default_tags = "1girl,"
        out_tags = default_tags + random_value
        print(f"随机lora:{random_value}")
        text_to_print = re.sub(pattern, out_tags, text_to_print)  # 将 随机 替换为新值

        # print(f"loraData_dict:{loraData_dict}")
        # print(f"loraData:{loraData}")
    else:
        # print("不存在 随机")
        print()

    # 再来一张
    global last_text_to_print

    if 'last_text_to_print' not in globals() or last_text_to_print is None:
        last_text_to_print = ""

    if text_to_print == "再来一张" or "re@" in text_to_print:
        text_to_print = last_text_to_print
        print("再来一张")

    last_text_to_print = text_to_print  # 存储上一张tag

    pattern = r"Negative prompt:"
    match = re.search(pattern, text_to_print)

    if match:
        print("存在 Negative prompt")
        # sdwebui格式参数，调用转换函数
        method = 1
        # 调用转换函数
        text_to_print = changeInfo(text_to_print, method)
    else:
        # print("不存在 Negative prompt")
        print()

    # 分割成三个部分
    parts = text_to_print.split(",")

    pattern = r"(.*?)(?=Steps:|Sampler:|CFG scale:|Seed:|Size:|数量:|sl:|高清:|Hires upscaler:|Hr scale:|Hires resize:|Hires steps:|Denoising strength:|ntags:|$)"
    match = re.search(pattern, text_to_print)
    ht_text = match.group(1).strip() if match else text_to_print.strip()
    # 没有逗号结尾则添加逗号
    ht_text = add_comma(ht_text)
    # print(ht_text)
    ht_text = match_lora(ht_text)

    param_text = ",".join(parts).strip() if len(parts) > 1 else ""

    # 分割字符串
    segments = text_to_print.split("ntags:")

    # 获取参数值
    steps = defaultSteps
    sampler = defaultSampler_index
    cfg_scale = defaultCfg_scale
    seed = defaultSeed
    size = defaultSize
    enable_hr = bool(defaultEnable_hr)
    hr_scale = int(defaultHr_scale)  # 放大倍数
    hr_resize_x = defaultHr_resize_x
    hr_resize_y = defaultHr_resize_y
    hr_upscaler = defaultHr_upscaler  # 放大算法
    hr_second_pass_steps = defaultHr_second_pass_steps  # 放大采样次数
    denoising_strength = defaultDenoising_strength  # 重绘幅度
    counts = 1

    #  解析中间参数
    if param_text:
        param_parts = param_text.split(",")
        for part in param_parts:
            key_value = part.split(":")
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Steps":
                    steps = value
                elif key == "Sampler":
                    sampler = value
                elif key == "CFG scale":
                    cfg_scale = value
                elif key == "Seed":
                    seed = value
                elif key == "Size":
                    size = value
                elif key == "Enable_hr":  # 高清开关
                    enable_hr = bool(value)
                elif key == "高清":
                    if value == "开":
                        enable_hr = bool("true")
                elif key == "Hires upscaler":  # 放大算法
                    hr_upscaler = value
                    if value is not None:
                        enable_hr = bool("true")
                elif key == "Hr scale":  # 放大倍数
                    hr_scale = value
                    if value is not None:
                        enable_hr = bool("true")
                elif key == "Hires resize":  # 放大宽高
                    hr_size = value.split("x")
                    hr_resize_x = int(hr_size[0])
                    hr_resize_y = int(hr_size[1])
                    if value is not None:
                        if hr_scale is None:
                            hr_scale = 2
                        enable_hr = bool("true")
                        width = int(hr_resize_x / hr_scale)
                        height = int(hr_resize_y / hr_scale)
                        size = f"{width}x{height}"
                elif key == "Hires steps":  # 放大采样步数 elif key == "Hr_second_pass_steps":
                    hr_second_pass_steps = value
                    if value is not None:
                        enable_hr = bool("true")
                elif key == "Denoising strength":  # 好像没有超分的也会有这个参数，重绘幅度 elif key == "Denoising_strength":
                    denoising_strength = value
                    if value is not None:
                        enable_hr = bool("true")
                elif key == "数量" or key == "sl":
                    counts = int(value)
                    if counts >= 10:
                        counts = 10
                    print(f"数量:{counts}")

    # 获取分割后的结果
    ntags = segments[1] if len(segments) > 1 else ""

    if ntags:
        # print("自定义ntags")
        print("")
    else:
        # print("ntags 为空")
        ntags = defaultNegative_prompt

    size = size.split("x")
    width = int(size[0])  # 512
    height = int(size[1])  # 768

    # defaultHr_scale = 2  # 默认超分倍率

    # print(enable_hr)
    # print(type(enable_hr))
    #
    # print("defaultHr_scale的类型")
    # print(type(defaultHr_scale))

    if enable_hr:
        # print("开启超分")
        hr_resize_x = int(width * hr_scale)
        hr_resize_y = int(height * hr_scale)

    print("正面(ht_text):", ht_text)
    print("步数(Steps):", steps)
    print("采样方法(Sampler):", sampler)
    print("相关性(CFG scale):", cfg_scale)
    print("种子(Seed):", seed)
    print("大小(Size):", size)
    print("负面(ntags):", ntags)
    print("放大开关(enable_hr):", enable_hr)
    print("放大算法(Hires upscaler):", hr_upscaler)
    print("放大倍数(Hr scale):", hr_scale)
    print("hr_resize_x:", hr_resize_x)
    print("hr_resize_y:", hr_resize_y)
    print("放大采样次数(hr_second_pass_steps):", hr_second_pass_steps)
    print("重绘幅度(denoising_strength):", denoising_strength)

    print("\n")

    payload = {
        "prompt": ht_text,
        "steps": steps,
        "negative_prompt": ntags,
        "seed": seed,
        "sampler_index": sampler,
        "width": width,
        "height": height,
        "cfg_scale": cfg_scale,
        "enable_hr": enable_hr,
        "hr_scale": hr_scale,
        "hr_upscaler": hr_upscaler,
        "hr_second_pass_steps": hr_second_pass_steps,
        "hr_resize_x": hr_resize_x,
        "hr_resize_y": hr_resize_y,
        "denoising_strength": denoising_strength,
        # "override_settings": {"sd_model_checkpoint": "perfectWorld_v3Baked.safetensors [0f49d1caa2]"},
        # "override_settings": {"sd_model_checkpoint": "AbyssOrangeMix2_nsfw.safetensors [0873291ac5]"},
        # "override_settings": {"sd_model_checkpoint": "cp6Mix.safetensors[9aeac6adf8]"},
    }
    print("正在绘图")
    time_start0 = tm.time()
    for _ in range(counts):
        print(f"循环执行{_ + 1}次")
        # 计时开始
        time_start = tm.time()
        response = requests.post(url=f'{localurl}/sdapi/v1/txt2img', json=payload)

        r = response.json()
        time_end = tm.time()
        time_c = time_end - time_start
        print("\n")
        time_text = f"总共耗时{time_c}s"
        print(time_text)

        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{localurl}/sdapi/v1/png-info', json=png_payload)
            # 图片参数
            info = response2.json().get("info")
            # print(f"图片参数:{info}")

            method = 2
            outInfo = changeInfo(info, method)

            # 保存图片参数
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))

            # 获取已存在文件中的最大编号
            existing_files = os.listdir(temp_dir)
            existing_numbers = [
                int(filename.split("-")[0])
                for filename in existing_files
                if filename.endswith(".png") and "-" in filename
            ]
            max_number = max(existing_numbers) if existing_numbers else -1
            # 生成文件名
            next_number = max_number + 1

            # 裁剪文件名
            shortened_text = ht_text[:max_filename_length - len(f'{next_number:05d}-') - len('.png')]
            # 删除非法字符
            filename = re.sub(r'[<>:"/\\|?*]', '', shortened_text)
            filename = f'{next_number:05d}-{filename}.png'
            print(f"保存图片:{filename}")
            temp_file = os.path.join(temp_dir, filename.replace("\\", "/"))  # 使用正斜杠 / 替换生成的文件路径中的反斜杠 \，以确保路径的正确性
            temp_file = temp_file.replace("\\", "/")
            # print(f"temp_file:{temp_file}")

            # 保存图片
            image.save(temp_file, 'PNG', pnginfo=pnginfo)
            # print(temp_file)

            # 构建发送图片的 API URL
            url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'

            # 发送图片给聊天 ID
            if message_thread_id is None:
                res = send_message(text=None, chat_id=chat_id, message_thread_id=None, temp_file=temp_file)
            else:
                res = send_message(text=None, chat_id=chat_id, message_thread_id=message_thread_id, temp_file=temp_file)

            # print("发送图片完成")

            # 这条信息的json
            data = res.json()
            # print(data)
            print(f"第{_ + 1}张图片完成")

            # 提取 message_id 值,获取回复消息的 ID
            message_id = data['result']['message_id']
            # print("Message ID:", message_id)
            # print("发送参数")
            # printInfo = f"绘图参数:\n{outInfo}\n{time_text}"
            printInfo = f"{outInfo}"
            if message_thread_id is None:
                res = requests.post(
                    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&reply_to_message_id={message_id}&text={printInfo}")
            else:
                res = requests.post(
                    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&reply_to_message_id={message_id}&text={printInfo}&message_thread_id={message_thread_id}")

            print("\n")
    print("全部绘图完成")
    time_end = tm.time()
    time_c = time_end - time_start0
    print("\n")
    time_text = f"{counts}张，总共耗时{time_c}s,/htre"
    # time_text = f"{counts}张，总共耗时{time_c}s\n/ht {text_to_print}"
    print(time_text)
    if message_thread_id is None:
        send_message(time_text, chat_id, message_thread_id=None, temp_file=None)
    else:
        send_message(time_text, chat_id, message_thread_id, temp_file=None)


# 帮助
def help(chat_id, message_thread_id):
    print("发送帮助信息")
    text = "发送/ht +你的绘图参数。例如：/ht (eyewear_on_head: 1.2), (rating:safe: 1.2), (1girl: 1.2), (sunglasses: 1.2), (purple_hair), (gloves), (solo), jacket, holding, purple_eyes, blurry, breasts, phone, shirt, belt, cellphone, upper_body, blurry_background, bangs, sidelocks, white_shirt, long_hair, long_sleeves, looking_at_viewer, smartphone, closed_mouth, red_gloves, expressionless, hair_between_eyes, black_jacket, jacket_on_shoulders,Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 7.0, Seed: 613188881, Size: 512x768, Enable_hr:True,ntags: paintings, sketches, (worst quality:2),(low quality:2), (extra fingers:2), (extra toes:2),bad-picture-chill-75v, badhandv4, easynegative, negative_hand-neg, ng_deepnegative_v1_75t" \
           "\n\n参数后面接':'，例如'Steps: 28'。目前可修改参数Steps（步数）、Sampler（采样方式）、CFG scale（相关性）、Seed（种子）、Size（图片大小）、Enable_hr（为true开启超分辨率，同时支持中文“高清：开”）、ntags（负面词）、sl：10（一次生成多图）。可以中英文符号混用。" \
           "\n请注意ntags要放在最后。不使用这些参数也能正常绘图。" \
           "\n\n发送'/ht 随机'可以使用随机lora。" \
           "\n\n发送'/lora+数字'可以查看lora" \
           "\n\n发送'/ht 再来一张'或者点击'/htre'可以用上一个词条生成"
    if message_thread_id is None:
        send_message(text, chat_id, message_thread_id=None, temp_file=None)
    else:
        send_message(text, chat_id, message_thread_id, temp_file=None)


# 根据指定的页数，输出对应页的内容
def print_page(chat_id, page_number, message_thread_id):
    global pages
    global total_pages

    if 0 < page_number <= total_pages:
        page_content = '\n'.join(pages[page_number - 1])
        out_text = f"第{page_number}页，共{total_pages}页\n\n{page_content}"
        if message_thread_id is None:
            res = send_message(out_text, chat_id, message_thread_id=None, temp_file=None)
        else:
            res = send_message(out_text, chat_id, message_thread_id, temp_file=None)
        print(f"发送第{page_number}页")
        # print(page_content)
        # data = res
        # print(data)
    else:
        print("Invalid page number")
        out_text = f"超出范围，共{total_pages}页"
        if message_thread_id is None:
            res = send_message(out_text, chat_id, message_thread_id=None, temp_file=None)
        else:
            res = send_message(out_text, chat_id, message_thread_id, temp_file=None)


def main():
    print("欢迎使用SDTGBOT")
    print("From https://github.com/1803233552/StableDiffusionTelegramBot")
    print("By DW_1803233552")
    print("\n")
    # 读取配置
    load_config()
    print("\n")
    print("开始监听")
    print("\n")

    # 加载lora数据
    read_lora(loraPath, loraFilename)
    loraData_dict = load_lora(loraFilename)
    load_loradata()
    # print(f"预设：{loraData_dict}")

    session = requests.Session()
    session.trust_env = True

    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    offset = None

    # 获取当前的最新消息的更新 ID
    response = session.get(url)
    data = response.json()
    if data['ok'] and data['result']:
        offset = data['result'][-1]['update_id'] + 1

    while True:
        try:
            # print("发送请求")
            params = {'offset': offset, 'timeout': 30}
            response = session.get(url, params=params)
            data = response.json()
            message_thread_id = None

            if data['ok'] and data['result']:
                for result in data['result']:
                    update_id = result['update_id']
                    message = result.get('message')
                    if message:
                        print(message)
                        chat_id = str(message['chat']['id'])

                        try:
                            # print(chat_id)
                            # 判断白名单是否为空，不为空则过滤
                            # if CHAT_ID:
                            #     # 判断群组或个人是否在白名单
                            #     if chat_id not in CHAT_ID:
                            #         print("不在白名单")
                            #         text = "没有权限"
                            #         # 发送消息
                            #         res = send_message(text, chat_id, message_thread_id=None, temp_file=None)
                            #         # 更新 offset 为最新的 update_id + 1，以排除已处理的消息
                            #         offset = update_id + 1
                            #         continue  # 跳过该消息，继续处理下一条消息

                            if message and 'message_thread_id' in message:
                                message_thread_id = message['message_thread_id']
                            else:
                                message_thread_id = None
                            print(f"message_thread_id {message_thread_id}")

                            # 判断白名单是否为空，不为空则过滤
                            if CHAT_ID:
                                # 判断群组或个人是否在白名单
                                if chat_id not in CHAT_ID:
                                    # 判断是否为群组
                                    # message_thread_ids = [106, 2]  # 替换为你要检测的message_thread_id
                                    message_thread_ids = [2]
                                    # 判断message是否存在并鉴权
                                    if message_thread_id is not None:

                                        # 判断message_thread_id白名单是否存在，以及是否在白名单
                                        if message_thread_ids:
                                            if message_thread_id not in message_thread_ids:
                                                # 在这里处理不存在于message_thread_ids中的message_thread_id
                                                # 你可以调用相应的函数或执行特定的操作
                                                # ...
                                                print("不在白名单")
                                                print(
                                                    f"message_thread_id {message_thread_id} 不存在于message_thread_ids中")
                                                text = "没有权限"
                                                # 发送消息
                                                res = send_message(text, chat_id, message_thread_id, temp_file=None)
                                                # 更新 offset 为最新的 update_id + 1，以排除已处理的消息
                                                offset = update_id + 1
                                                continue  # 跳过该消息，继续处理下一条消息

                                            # 存在于白名单中的message_thread_id，不做处理

                                        # 白名单为空，不做处理

                                    else:
                                        # 在这里不存在message_thread_id，不做处理
                                        # print(message)
                                        print()

                                        print("不在群组白名单")
                                        text = "没有权限"
                                        # 发送消息
                                        res = send_message(text, chat_id, message_thread_id=None, temp_file=None)
                                        # 更新 offset 为最新的 update_id + 1，以排除已处理的消息
                                        offset = update_id + 1
                                        continue  # 跳过该消息，继续处理下一条消息

                                # 在群组白名单中，不做处理

                            # 白名单为空，不做处理

                            text = message.get('text')
                            # 获取消息发送者的信息
                            from_user = message.get('from')
                            if not from_user:
                                continue  # 跳过该消息，继续处理下一条消息
                            is_bot = from_user.get('is_bot')
                            username = from_user.get('username')

                            # 检查消息是否来自机器人本身
                            if is_bot and username == 'YOUR_BOT_USERNAME':
                                continue  # 跳过该消息，继续处理下一条消息

                            if text:
                                # print("最新的消息文本值：", text)
                                # 绘图指令判断
                                if text.startswith('/ht'):
                                    text_to_print = text[3:]  # 获取 "/绘图" 后面的文本
                                    print("收到绘图指令，文本内容：", text_to_print)

                                    # ... 绘图的其他代码 ...
                                    draw(text_to_print, chat_id, message_thread_id)

                                # 帮助指令判断
                                if text.startswith('/help'):
                                    help(chat_id, message_thread_id)

                                # lora指令判断
                                if text.startswith('/lora'):
                                    page_number = text[5:]  # 获取 "/绘图" 后面的文本
                                    print("收到lora指令，文本内容：", page_number)

                                    # 检查变量类型
                                    if isinstance(page_number, str):
                                        print("变量是字符串")
                                        # 尝试将字符串转换为整数
                                        try:
                                            page_number = int(page_number)
                                            print("变量已成功转换为整数")
                                        except ValueError:
                                            # 如果无法转换为整数，则尝试将字符串转换为浮点数
                                            try:
                                                page_number = float(page_number)
                                                print("变量已成功转换为浮点数")
                                                page_number = round(page_number)  # 四舍五入
                                                page_number = int(page_number)  # 转换为整数
                                            except ValueError:
                                                print("无法将变量转换为数字类型，设置默认值1")
                                                # 设置默认值
                                                page_number = 1
                                    elif isinstance(page_number, int) or isinstance(page_number, float):
                                        print("变量是数字")
                                    else:
                                        print("变量不是字符串也不是数字")

                                    # 输出转换后的结果
                                    print("转换后的变量类型：", type(page_number))
                                    print("转换后的变量值：", page_number)

                                    if page_number is None or page_number == "":
                                        page_number = 1
                                        # 输出lora列表
                                        print_page(chat_id, page_number, message_thread_id)
                                    elif page_number == "1":
                                        print_page(chat_id, int(1), message_thread_id)
                                    else:
                                        print_page(chat_id, int(page_number), message_thread_id)

                            # 更新 offset 为最新的 update_id + 1，以排除已处理的消息
                            offset = update_id + 1

                        except Exception as e:
                            print("处理消息时发生错误：", str(e))

                            text = f"处理消息时发生错误：{str(e)}"
                            if message_thread_id is None:
                                send_message(text, chat_id, message_thread_id=None, temp_file=None)
                            else:
                                send_message(text, chat_id, message_thread_id, temp_file=None)

                            # 更新 offset 为最新的 update_id + 1，以排除已处理的消息
                            offset = update_id + 1
                            continue  # 跳过该消息，继续处理下一条消息
                            # break  # 停止处理消息，跳出循环

        except Exception as e:
            print("获取消息时发生错误：", str(e))
            # 处理异常并进行适当的错误处理。
            # break  # 停止处理消息，跳出循环  这里break会结束程序


# 程序入口
if __name__ == '__main__':
    main()
