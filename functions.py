def visual_delta(td):
    delta = [
        ("дн", td.days),
        ("ч", td.seconds // 3600),
        ("мин", td.seconds % 3600 // 60),
        ("сек", td.seconds % 60)
    ]
    out = ""
    for kw, v in delta:
        if v != 0:
            out += f"{v} {kw} "
    return "0 сек" if out == "" else out.strip()