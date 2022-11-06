from typing import Any, List, Tuple
from PIL import Image
import json
import base64
from io import BytesIO
import sqlite3
import hashlib

SPEED_CONSTANT = 2
INSTANT_WAIT_TIME = 1
STORAGE_SIZE = 0.025

scale_bundle = lambda scale: {
    "scale": scale,
    "defaultScale": scale,
    "homescale": scale,
}

shown_bundle = lambda shown: {
    "shown": shown,
    "homeshown": shown,
}


class Sprite:
    curr_id = 0

    def __init__(
        self,
        xcoor: int,
        ycoor: int,
        texture_id: str,
        width: int = 50,
        height: int = 50,
        **kwargs,
    ):
        self.id = f"ID{Sprite.curr_id}"
        Sprite.curr_id += 1
        self.x = xcoor
        self.y = ycoor
        self.texture = texture_id
        self.width = width
        self.height = height
        self.scripts = []
        self.object_out = {
            "shown": True,
            "type": "sprite",
            "md5": self.texture,
            "id": self.id,
            "flip": False,
            "name": self.id,
            "angle": 0,
            "scale": 0.5,
            "speed": 2,
            "defaultScale": 0.5,
            "sounds": ["pop.mp3"],
            "xcoor": self.x,
            "ycoor": self.y,
            "cx": self.width // 2,
            "cy": self.height // 2,
            "w": self.width,
            "h": self.height,
            "homex": self.x,
            "homey": self.y,
            "homescale": 0.5,
            "homeshown": True,
            "homeflip": False,
            "scripts": self.scripts,
        }
        for key, value in kwargs.items():
            self.object_out[key] = value

    def get_object(self):
        return self.object_out

    def add_script(self, script):
        new_script = [i.get_list_form() for i in script]
        self.scripts.append(new_script)

    def add_scripts(self, scripts):
        for i in scripts:
            self.add_script(i)


class Page:
    current_page = 1

    def __init__(self, image=None, name=None):
        self.num = Page.current_page
        if name == None:
            Page.current_page += 1
            self.name = f"page {self.num}"
        else:
            self.name = name
        self.sprites = []

    def add_sprite(self, sprite):
        self.sprites.append(sprite)

    def get_object(self):
        object_out = {
            "sprites": [i.id for i in self.sprites],
            "layers": [i.id for i in self.sprites],
            "num": self.num,
        }
        for i in self.sprites:
            object_out[i.id] = i.get_object()
        return object_out


class Project:
    def __init__(self):
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)

    def get_object(self):
        object_out = {
            "pages": [i.name for i in self.pages],
            "currentPage": self.pages[0].name,
        }
        for i in self.pages:
            object_out[i.name] = i.get_object()

        return object_out


class ScriptElement:
    """
    Valid Actions Include:
    onflag
    onclick
    ontouch
    onmessage string(color?)
    message string(color?)
    repeat int scriptlist
    forward int
    back int
    up int
    down int
    right int
    left int
    hop int
    home
    stopmine
    say string
    grow int
    shrink int
    same
    hide
    show
    playsnd string
    wait int
    setspeed int
    endstack
    forever
    gotopage int
    """

    def __init__(
        self,
        action: str,
        parameter: str | float = "null",
        script_parameter: List[Any] = [],
    ):
        self.action = action
        self.parameter = parameter
        self.script_parameter = script_parameter

    def get_list_form(self):
        object_out = [self.action, self.parameter, 50, 50]
        if self.action == "repeat":
            object_out.append([i.get_list_form() for i in self.script_parameter])
        return object_out


def get_bitmap_base64(x: int, y: int, color: Tuple[int, int, int] = (0, 0, 0)):
    im = Image.new("RGB", (x, y), tuple(color))
    buffered = BytesIO()
    im.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return str(img_str, "ascii")


def get_svg_base64(
    x: int, y: int, color: Tuple[int, int, int] = (0, 0, 0), text: str = ""
):
    im = f"""
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox= "0 0 {x} {y}" width="{x}px" height="{y}px">
    <!--Created with the Scratch Jr Wrapper-->
    <g xmlns="http://www.w3.org/2000/svg" id="layer1" style="pointer-events:visiblePainted">
    <path d="M 0 0 H {x} V {y} H 0 Z" id="path 1" opacity="1" fill="rgb{str(tuple(color))}" stroke="none" stroke-width="2" stroke-linecap="round" style="pointer-events:visiblePainted;" transform="rotate(0)"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle">{text}</text>
    </g>
    </svg>
    """
    img_str = base64.b64encode(im.encode())
    return str(img_str, "ascii")


def get_generic_image_base64(
    x: int,
    y: int,
    color: Tuple[int, int, int] = (0, 0, 0),
    text: str = "",
    svg: bool = True,
):
    if svg:
        return get_svg_base64(x, y, color, text)
    else:
        return get_bitmap_base64(x, y, color)


def get_systematic_image_name(
    width: int,
    height: int,
    color: Tuple[int, int, int] = (0, 0, 0),
    text: str = "",
    svg: bool = True,
):
    object_out = str(("systematic scrach mmlib", width, height, text, tuple(color)))
    hash_str = hashlib.md5(object_out.encode()).hexdigest()
    return hash_str + (".svg" if svg else ".png")


# def register_image_cursor(
#     cursor: sqlite3.Cursor, image_data: Any, file_ending: str = "svg"
# ):
#     pass


def get_shape_from_cursor(
    cursor: sqlite3.Cursor,
    width: int,
    height: int,
    color: Tuple[int, int, int] = (0, 0, 0),
    text: str = "",
    svg=True,
):
    file_name = get_systematic_image_name(width, height, color, text, svg)
    if (
        len(
            list(
                cursor.execute(
                    f"SELECT MD5 FROM PROJECTFILES WHERE MD5 = '{file_name}'"
                )
            )
        )
        == 0
    ):
        cursor.execute(
            f"INSERT INTO PROJECTFILES (MD5, CONTENTS) VALUES ('{file_name}','{get_generic_image_base64(width,height,color, text, svg)}')"
        )
        print(f"Created new file '{file_name}'.")
    else:
        print(f"Found file '{file_name}'.")
    return file_name


def set_project_json(cursor: sqlite3.Cursor, name: str, project: Project):
    """Sets the JSON data of the named project in to that of the passed project through the cursor."""
    sanitized_json = json.dumps(project.get_object()).replace("'", "''")
    cursor.execute(
        f"UPDATE PROJECTS SET JSON = '{sanitized_json}' WHERE NAME = '{name}'"
    )


def get_project_json(cursor: sqlite3.Cursor, name: str) -> str:
    try:
        return cursor.execute(
            f"SELECT JSON FROM PROJECTS WHERE NAME = '{name}'"
        ).fetchall()[0]
    except IndexError:
        raise Exception(f'Project "{name}" does not exist!')


def example():
    connection_path = input("Please input the path of your database file: ")

    if connection_path == "":
        connection_path = "/Users/rick/Documents/ScratchJR/scratchjr.sqllite"

    conn = sqlite3.connect(connection_path)
    cursor = conn.cursor()

    project_name = input("Please input the project's name: ")

    sprite_text = input("Please input the sprite's text: ")

    sprite_say = input("Please input what the sprite will say: ")

    sprite_times = int(input("Please input how many times the sprite will say it: "))

    my_project = Project()
    my_page = Page()
    my_sprite = Sprite(
        100,
        100,
        get_shape_from_cursor(cursor, 50, 50, (52, 86, 139), sprite_text),
        50,
        50,
    )

    my_project.add_page(my_page)
    my_page.add_sprite(my_sprite)

    my_sprite.add_script(
        [
            ScriptElement("onflag"),
            ScriptElement("repeat", sprite_times, [ScriptElement("say", sprite_say)]),
            ScriptElement("endstack"),
        ]
    )

    set_project_json(cursor, project_name, my_project)

    print(f"Final project JSON: {json.dumps(my_project.get_object())}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    example()
