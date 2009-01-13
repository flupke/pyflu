colors = {
    "default": 0, 
    "black":30, 
    "red":31, 
    "green":32, 
    "yellow":33,
    "blue":34,
    "magenta":35, 
    "cyan":36, 
    "white":37, 
    "black":38,
    "black":39
}


def colorize(text, color, bright=False, default_color="default"):
    if bright:
        bright_int = 1
    else:
        bright_int = 0
    c1 = colors[color]
    c2 = colors[default_color]
    return "\033[%d;%dm%s\033[%dm" % (bright_int, c1, text, c2)
