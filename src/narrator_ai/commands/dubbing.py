"""Pre-built dubbing (voice) resources for task creation."""

from typing import Optional

import typer

from narrator_ai.output import console, print_error, print_json, print_table

app = typer.Typer(
    help=(
        "Pre-built dubbing voices for task creation.\n\n"
        "Use the dubbing ID as 'dubbing' and the type as 'dubbing_type'\n"
        "in clip-data, fast-clip-data, or video-composing tasks.\n\n"
        "View voice previews: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc"
    ),
)

DUBBING_LIST = [
    # 普通话 - 角色/影视
    {"name": "霸王别姬-程蝶衣", "id": "MiniMaxVoiceId02586", "type": "普通话", "tag": "角色"},
    {"name": "酱园弄-詹周氏", "id": "MiniMaxVoiceId10985", "type": "普通话", "tag": "角色"},
    {"name": "不说话的爱-木木", "id": "MiniMaxVoiceId13064", "type": "普通话", "tag": "角色"},
    {"name": "聊斋", "id": "MiniMaxVoiceId12982", "type": "普通话", "tag": "角色"},
    {"name": "蜡笔小新", "id": "MiniMaxVoiceId14640", "type": "普通话", "tag": "角色"},
    {"name": "我是余欢水-余欢水", "id": "MiniMaxVoiceId15111", "type": "普通话", "tag": "角色"},
    {"name": "唐伯虎点秋香-唐伯虎", "id": "MiniMaxVoiceId17399", "type": "普通话", "tag": "角色"},
    {"name": "人生大事-莫三妹", "id": "MiniMaxVoiceId17438", "type": "普通话", "tag": "角色"},
    {"name": "夏洛特烦恼-沈腾", "id": "MiniMaxVoiceId17643", "type": "普通话", "tag": "角色"},
    # 普通话 - 通用男声
    {"name": "浑厚旁白", "id": "MiniMaxVoiceId15619", "type": "普通话", "tag": "通用男声"},
    {"name": "知心哥哥", "id": "MiniMaxVoiceId15944", "type": "普通话", "tag": "通用男声"},
    {"name": "解说男声", "id": "MiniMaxVoiceId15553", "type": "普通话", "tag": "通用男声"},
    {"name": "温暖男声", "id": "MiniMaxVoiceId16317", "type": "普通话", "tag": "通用男声"},
    {"name": "乐天派男声", "id": "MiniMaxVoiceId15847", "type": "普通话", "tag": "通用男声"},
    {"name": "阳光男声", "id": "MiniMaxVoiceId15390", "type": "普通话", "tag": "通用男声"},
    {"name": "深邃旁白", "id": "MiniMaxVoiceId15257", "type": "普通话", "tag": "通用男声"},
    {"name": "利落男声", "id": "MiniMaxVoiceId15047", "type": "普通话", "tag": "通用男声"},
    {"name": "激昂旁白", "id": "MiniMaxVoiceId14983", "type": "普通话", "tag": "通用男声"},
    # 普通话 - 场景推荐
    {"name": "严肃大叔音-适合动作、冒险类", "id": "mercury_yunye_24k@serious", "type": "普通话", "tag": "动作冒险"},
    {"name": "严肃青年解说-适合动作、冒险类", "id": "mercury_yunxi_24k@serious", "type": "普通话", "tag": "动作冒险"},
    {"name": "气泡音男声-适合动作、冒险类", "id": "momoyuan_meet_24k", "type": "普通话", "tag": "动作冒险"},
    {"name": "慵懒调侃男声-适合动作、冒险类", "id": "jupiter_BV107DialogMale", "type": "普通话", "tag": "动作冒险"},
    {"name": "神秘女声-适合动作、冒险、恐怖、惊悚类", "id": "galaxy_fastv7_moyingxi@angry", "type": "普通话", "tag": "动作冒险"},
    {"name": "东北老妹儿-适合喜剧", "id": "mercury_ln-xiaobei_24k", "type": "普通话", "tag": "喜剧"},
    {"name": "幽默闲聊女声-适合喜剧", "id": "galaxy_fastv8_moxueqin", "type": "普通话", "tag": "喜剧"},
    {"name": "犀利青年音-适合喜剧", "id": "galaxy_fastv8_mowasi", "type": "普通话", "tag": "喜剧"},
    {"name": "恐惧感大叔音-适合恐怖、惊悚类", "id": "mercury_yunye_24k@fearful", "type": "普通话", "tag": "恐怖惊悚"},
    {"name": "恐惧低沉大叔音-适合恐怖、惊悚类", "id": "mercury_yunze_24k@fearful", "type": "普通话", "tag": "恐怖惊悚"},
    {"name": "不安男声-适合恐怖、惊悚类、科幻", "id": "mercury_yunxi_48k@embarrassed", "type": "普通话", "tag": "恐怖惊悚"},
    {"name": "松弛大叔音-适合爱情、剧情类", "id": "mercury_yunyang_24k@newscast", "type": "普通话", "tag": "爱情剧情"},
    {"name": "元气少女音-适合爱情、剧情类", "id": "mercury_xiaochen_48k", "type": "普通话", "tag": "爱情剧情"},
    {"name": "磁性御姐音-适合爱情、剧情类", "id": "yangjingv_meet_24k", "type": "普通话", "tag": "爱情剧情"},
    {"name": "燃爆男声解说-适合爱情、剧情类", "id": "mercury_yunxi_24k", "type": "普通话", "tag": "爱情剧情"},
    {"name": "快嘴直爽青年-适合科幻类", "id": "moxidu_meet_24k@kehuan", "type": "普通话", "tag": "科幻"},
    {"name": "磁性悬疑男声-适合科幻类", "id": "manchaozn_meet_24k@boya", "type": "普通话", "tag": "科幻"},
    {"name": "冷静青年解说-适合历史、战争类", "id": "mercury_yunxi_48k@calm", "type": "普通话", "tag": "历史战争"},
    {"name": "沉稳大叔音-适合历史、战争类", "id": "mercury_yunze_24k@documentary-narration", "type": "普通话", "tag": "历史战争"},
    {"name": "纪实磁性男声-适合历史、战争类", "id": "manchaozn_meet_24k@jilupian", "type": "普通话", "tag": "历史战争"},
    {"name": "沉稳御姐音-适合历史、战争类", "id": "liyuansong_meet_24k@tale", "type": "普通话", "tag": "历史战争"},
    # 英语
    {"name": "英语-腔调青年音", "id": "mercury_guy_48k", "type": "英语", "tag": "英语"},
    {"name": "英语-温柔御姐音", "id": "chilli_meet_24k", "type": "英语", "tag": "英语"},
    {"name": "英语-慵懒少年音", "id": "arielturner_meet_24k", "type": "英语", "tag": "英语"},
    {"name": "英语-儒雅大叔", "id": "mandygubler_meet_24k", "type": "英语", "tag": "英语"},
    # 日语
    {"name": "日语-元气少女音", "id": "galaxy_fastmultiv1_moyouli", "type": "日语", "tag": "日语"},
    {"name": "日语-中年男声", "id": "galaxy_fastmultiv1_mozhishu", "type": "日语", "tag": "日语"},
    {"name": "日语-沧桑大叔音", "id": "mercury_naoki_24k", "type": "日语", "tag": "日语"},
    # 韩语
    {"name": "韩语-儒雅男声", "id": "mercury_injoon_24k", "type": "韩语", "tag": "韩语"},
    {"name": "韩语-温柔御姐音", "id": "mercury_sunhi_48k", "type": "韩语", "tag": "韩语"},
    # 西班牙语
    {"name": "西班牙语-温柔女声", "id": "mercury_dalia_48k", "type": "西班牙语", "tag": "西班牙语"},
    {"name": "西班牙语-温柔大叔音", "id": "mercury_jorge_48k", "type": "西班牙语", "tag": "西班牙语"},
    {"name": "西班牙语-磁性大叔音", "id": "mercury_alvaro_24k", "type": "西班牙语", "tag": "西班牙语"},
    # 葡萄牙语
    {"name": "葡萄牙语-沉稳男声", "id": "mercury_donato_24k", "type": "葡萄牙语", "tag": "葡萄牙语"},
    {"name": "葡萄牙语-热情女声", "id": "mercury_francisca_48k", "type": "葡萄牙语", "tag": "葡萄牙语"},
    # 德语
    {"name": "德语-稳重大叔音", "id": "mercury_christoph_48k", "type": "德语", "tag": "德语"},
    {"name": "德语-气质御姐音", "id": "mercury_katja_48k", "type": "德语", "tag": "德语"},
    # 法语
    {"name": "法语-慵懒大叔音", "id": "mercury_alain_24k", "type": "法语", "tag": "法语"},
    {"name": "法语-优雅女神音", "id": "mercury_brigitte_24k", "type": "法语", "tag": "法语"},
    # 阿拉伯语
    {"name": "阿拉伯语-稳重御姐音", "id": "mercury_salma_48k", "type": "阿拉伯语", "tag": "阿拉伯语"},
    {"name": "阿拉伯语-慵懒男低音", "id": "mercury_hamdan_24k", "type": "阿拉伯语", "tag": "阿拉伯语"},
    # 泰语
    {"name": "泰语-撩耳解说男音", "id": "mercury_niwat_24k", "type": "泰语", "tag": "泰语"},
    {"name": "泰语-气质御姐音", "id": "mercury_premwadee_24k", "type": "泰语", "tag": "泰语"},
    # 印尼语
    {"name": "印尼语-青年男声", "id": "mercury_ardi_24k", "type": "印尼语", "tag": "印尼语"},
    {"name": "印尼语-温柔御姐音", "id": "mercury_gadis_48k", "type": "印尼语", "tag": "印尼语"},
]


@app.command("list")
def list_dubbing(
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by language/dubbing_type (e.g. 普通话, 英语, 日语)"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag (e.g. 喜剧, 恐怖惊悚, 角色, 通用男声)"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search by voice name"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List pre-built dubbing voices.

    Use the 'id' as 'dubbing' and 'type' as 'dubbing_type' in task creation.

    View voice previews: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc
    """
    items = DUBBING_LIST
    if lang:
        items = [d for d in items if lang in d["type"]]
    if tag:
        items = [d for d in items if tag in d["tag"]]
    if search:
        items = [d for d in items if search.lower() in d["name"].lower()]

    if not items:
        print_error("No voices found. Use --lang, --tag, or --search to filter.")
        raise typer.Exit(1)

    if json_mode:
        print_json(items)
    else:
        title_parts = ["Dubbing Voices"]
        if lang:
            title_parts.append(lang)
        if tag:
            title_parts.append(tag)
        title = f"{' - '.join(title_parts)} ({len(items)})"
        columns = [("name", "Voice"), ("id", "Dubbing ID"), ("type", "dubbing_type"), ("tag", "Tag")]
        print_table(items, columns, title=title)
        console.print(f"\n[dim]View previews: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc[/dim]")


@app.command("languages")
def list_languages(
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List available dubbing languages (dubbing_type values) with counts."""
    lang_counts = {}
    for d in DUBBING_LIST:
        lang_counts[d["type"]] = lang_counts.get(d["type"], 0) + 1
    items = [{"language": l, "count": c} for l, c in sorted(lang_counts.items())]

    if json_mode:
        print_json(items)
    else:
        print_table(items, [("language", "Language (dubbing_type)"), ("count", "Count")],
                    title=f"Dubbing Languages ({len(DUBBING_LIST)} voices)")


@app.command("tags")
def list_tags(
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List available voice tags (genre recommendations) with counts."""
    tag_counts = {}
    for d in DUBBING_LIST:
        tag_counts[d["tag"]] = tag_counts.get(d["tag"], 0) + 1
    items = [{"tag": t, "count": c} for t, c in sorted(tag_counts.items())]

    if json_mode:
        print_json(items)
    else:
        print_table(items, [("tag", "Tag"), ("count", "Count")],
                    title=f"Voice Tags ({len(DUBBING_LIST)} voices)")
