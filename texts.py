from dns import message


version = "2.0.0-beta.13"


class TextFields:
    """文本"""
    command_help = [f"""\
>> 命令一览
* 开发完善中

获取 Gravatar 头像: !!cht gravatar
MC 服务器状态: !!cht mcstatus

关于: !!cht info
命令一览: !!cht help
English: !!cht en help""",
                    f"""\
>> Commands review
* In dev

Get Gravatar images: !!cht en gravatar
MC server status: !!cht en mcstatus

About: !!cht en info
Commands review: !!cht en help

Add "en" before the command name to get an English version!
eg. [!!cht help] -> [!!cht en help]"""]

    info = [f"""\
Christina Network v{version}
一个小项目 希望为您带来便捷与快乐 :D
>> 2.x 开发中

Start from 2020.08.16 | By CursoR_光标""",
            f"""\
Christina Network v{version}
A tiny project that hopes to bring u convenience & happiness :D
>> Version 2.x in dev
* Not every commands have an English text, hope to understand

Start from 2020.08.16 | By CursoR_光标"""]

    need_params = ["""\
请传入参数!
使用 !!cht help 查看帮助""",
                   """\
Please pass in parameters!
Use [!!cht en help] to get helps"""]

    command_not_found = ["""\
指令不存在!
使用 !!cht help 查看帮助""",
                         """\
Command not found!
Use [!!cht en help] to get helps"""]

    gravatar_help = ["""\
>> 获取 Gravatar 头像
在群内通过命令查看用户的 Gravatar 头像

使用方法: !!cht gravatar {邮箱地址}
例 [!!cht gravatar christina@icursors.net]

* 仅支持获取 G 等级 分辨率 320*320 的头像""",
                     """\
>> Get Gravatar images
Use commands to get users' Gravatar images

Usage: !!cht en gravatar {EMAIL ADDR}
e.g [!!cht en gravatar christina@icursors.net]

* Only images [rated G] in 320px*320px are supported"""]

    gravatar_404 = [
        "该用户无 Gravatar 头像",
        "This user has no Gravatar image"
    ]

    global mcstatus_text
    mcstatus_text = [
        [
            "服务器运行中",
            "游戏版本",
            "在线玩家"
        ],
        [
            "Server online",
            "Game version",
            "Online player(s)"
        ]
    ]

    def mcstatus(lang, addr, ping, version, players_online, players_max, players_list):
        message = f"""\
[{addr}]
{mcstatus_text[lang][0]} [{ping}ms]
{mcstatus_text[lang][1]}: {version}
{mcstatus_text[lang][2]}: [{players_online}/{players_max}]{players_list}"""
        return message
    
    mcstatus_more = [
        "名其他玩家",
        "other players"
    ]

    mcstatus_not_set = ["""\
本群未设置 MC 服务器!
联系 CursoR_光标 添加 MC 服务器即可从群里获取服务器状态""",
                        """\
This group hasn't set an MC server yet!
Contact CursoR_光标 and set your MC server to use this command"""]

    mcstatus_error = ["""\
MC 服务器状态获取失败!
可能由于 服务器关闭 / 连接超时 / DNS 记录未生效 等
请稍后再试""",
                      """\
Get MC server status failed!
May caused by: Server offline / Connection timed out / DNS record not valid etc.
Please try again later"""]
