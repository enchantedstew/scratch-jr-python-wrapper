import scratchjr
from scratchjr import Page, Project, Sprite, ScriptElement, get_shape_from_cursor
import sqlite3
import json

SPEED_CONSTANT = 2
INSTANT_WAIT_TIME = 1
STORAGE_SIZE = 0.025


def create_project_beta(code: str, cursor: sqlite3.Cursor):
    scale_bundle = lambda scale: {
        "scale": scale,
        "defaultScale": scale,
        "homescale": scale,
    }

    shown_bundle = lambda shown: {
        "shown": shown,
        "homeshown": shown,
    }

    my_project = Project()
    my_page = Page()
    my_project.add_page(my_page)

    instruction = Sprite(
        50, 50, get_shape_from_cursor(cursor, 100, 100), 100, 100, **scale_bundle(1)
    )

    my_page.add_sprite(instruction)

    vars_block = {}

    reaction_sprite = Sprite(
        150,
        50,
        get_shape_from_cursor(cursor, 100, 100, (0, 0, 255)),
        100,
        100,
        **scale_bundle(1),
    )

    my_page.add_sprite(reaction_sprite)

    reaction_sprite.add_script(
        [ScriptElement("ontouch"), ScriptElement("message", "CustomMemoryHalt")]
    )

    commands = code.split("\n")

    commands = [i if i != "" else "c" for i in commands]

    for i, command in enumerate(commands, 1):

        parsed_values = {"type": None, "goto": i + 1, "increment": 1}

        next_val = None

        for character in command:
            match character:
                case _ if parsed_values["type"] in ("p", "c"):
                    if next_val not in parsed_values.keys():
                        parsed_values[next_val] = ""
                    parsed_values[next_val] += character
                case "+":
                    parsed_values["type"] = "+"
                    next_val = "address"
                case "-":
                    parsed_values["type"] = "-"
                    next_val = "address"
                case ">":
                    next_val = "elsegoto"
                case "|":
                    next_val = "goto"
                    parsed_values["goto"] = ""
                case "#":
                    next_val = "increment"
                    parsed_values["increment"] = ""
                case "r":
                    parsed_values["type"] = "r"
                    next_val = "address"
                case "p":
                    parsed_values["type"] = "p"
                    next_val = "text"
                case "c":
                    parsed_values["type"] = "c"
                    next_val = "comment"
                case _ if next_val == None:
                    raise Exception(
                        f"WHAT ARE YOU DOING IN LINE {i} AKA: {command}!?!?!"
                    )
                case _:
                    if next_val not in parsed_values.keys():
                        parsed_values[next_val] = ""
                    parsed_values[next_val] += character

        match parsed_values["type"]:
            case "+":

                instruction.add_script(
                    [
                        ScriptElement("onmessage", f"CustomExecute{i}"),
                        ScriptElement(
                            "message",
                            f"CustomIncrement{parsed_values['address']}From{i}",
                        ),
                        ScriptElement(
                            "message", f"CustomExecute{parsed_values['goto']}"
                        ),
                    ]
                )

                if parsed_values["address"] not in vars_block.keys():
                    vars_block[parsed_values["address"]] = Sprite(
                        150,
                        150,
                        get_shape_from_cursor(cursor, 100, 100, (0, 255, 0)),
                        100,
                        100,
                        **scale_bundle(1),
                    )

                vars_block[parsed_values["address"]].add_script(
                    [
                        ScriptElement(
                            "onmessage",
                            f"CustomIncrement{parsed_values['address']}From{i}",
                        ),
                        ScriptElement(
                            "repeat",
                            int(parsed_values["increment"]),
                            [ScriptElement("down", STORAGE_SIZE)],
                        ),
                    ]
                )

            case "-":
                instruction.add_scripts(
                    [
                        [
                            ScriptElement("onmessage", f"CustomExecute{i}"),
                            ScriptElement(
                                "message",
                                f"CustomDecrement{parsed_values['address']}From{i}",
                            ),
                            ScriptElement("wait", STORAGE_SIZE * SPEED_CONSTANT * 2),
                            ScriptElement(
                                "message",
                                f"CustomMemoryReset{parsed_values['address']}",
                            ),
                            ScriptElement(
                                "message",
                                f"CustomExecute{parsed_values['elsegoto']}",
                            ),
                        ],
                        [
                            ScriptElement("onmessage", f"CustomCallB{i}"),
                            ScriptElement("stopmine"),
                            ScriptElement(
                                "message", f"CustomExecute{parsed_values['goto']}"
                            ),
                        ],
                    ]
                )

                if parsed_values["address"] not in vars_block.keys():
                    vars_block[parsed_values["address"]] = Sprite(
                        150,
                        150,
                        get_shape_from_cursor(cursor, 100, 100, (0, 255, 0)),
                        100,
                        100,
                        **scale_bundle(1),
                    )

                vars_block[parsed_values["address"]].add_scripts(
                    [
                        [
                            ScriptElement(
                                "onmessage",
                                f"CustomDecrement{parsed_values['address']}From{i}",
                            ),
                            ScriptElement("up", STORAGE_SIZE),
                            ScriptElement("wait", INSTANT_WAIT_TIME),
                            ScriptElement("message", f"CustomCallB{i}"),
                        ],
                        [
                            ScriptElement("onmessage", "CustomMemoryHalt"),
                            ScriptElement("stopmine"),
                        ],
                        [
                            ScriptElement(
                                "onmessage",
                                f"CustomMemoryReset{parsed_values['address']}",
                            ),
                            ScriptElement("home"),
                        ],
                    ]
                )

            case "p":
                if "text" not in parsed_values.keys():
                    parsed_values["text"] = ""
                instruction.add_script(
                    [
                        ScriptElement("onmessage", f"CustomExecute{i}"),
                        ScriptElement("say", parsed_values["text"]),
                        ScriptElement(
                            "message", f"CustomExecute{parsed_values['goto']}"
                        ),
                    ]
                )
            case "r":
                instruction.add_script(
                    [
                        ScriptElement("onmessage", f"CustomExecute{i}"),
                        ScriptElement(
                            "message",
                            f"CustomMemoryReset{parsed_values['address']}",
                        ),
                        ScriptElement(
                            "message", f"CustomExecute{parsed_values['goto']}"
                        ),
                    ]
                )

                if parsed_values["address"] not in vars_block.keys():
                    vars_block[parsed_values["address"]] = Sprite(
                        150,
                        150,
                        get_shape_from_cursor(cursor, 100, 100, (0, 255, 0)),
                        100,
                        100,
                        **scale_bundle(1),
                    )

                vars_block[parsed_values["address"]].add_script(
                    [
                        ScriptElement(
                            "onmessage",
                            f"CustomMemoryReset{parsed_values['address']}",
                        ),
                        ScriptElement("home"),
                    ]
                )
            case "c":
                instruction.add_script(
                    [
                        ScriptElement("onmessage", f"CustomExecute{i}"),
                        ScriptElement(
                            "message", f"CustomExecute{parsed_values['goto']}"
                        ),
                    ]
                )

    for i in vars_block.values():
        my_page.add_sprite(i)

    instruction.add_script(
        [ScriptElement("onflag"), ScriptElement("message", "CustomExecute1")]
    )

    if "0" not in vars_block.keys():
        vars_block["0"] = Sprite(
            150,
            150,
            get_shape_from_cursor(cursor, 100, 100, (0, 255, 0)),
            100,
            100,
            **scale_bundle(1),
        )
        my_page.add_sprite(vars_block["0"])

    vars_block["0"].add_scripts(
        [
            [
                ScriptElement("onmessage", "CustomInputIncrement"),
                ScriptElement("down", STORAGE_SIZE),
            ],
            [ScriptElement("onmessage", "CustomInputReset"), ScriptElement("home")],
        ]
    )

    for i in range(10):
        temp = Sprite(
            (i % 10) * 10 + 305,
            (i // 10) * 10 + 5,
            get_shape_from_cursor(cursor, 10, 10, (0, 255, 255), i),
            10,
            10,
            **scale_bundle(1),
        )
        my_page.add_sprite(temp)
        temp.add_script(
            [
                ScriptElement("onclick"),
                ScriptElement("message", "CustomInputReset"),
                ScriptElement(
                    "repeat", i, [ScriptElement("message", "CustomInputIncrement")]
                )
                if i != 0
                else ScriptElement("endstack"),
            ]
        )

    return my_project


def main():
    conn = sqlite3.connect("/Users/rick/Documents/ScratchJR/scratchjr.sqllite")
    cursor = conn.cursor()

    ia_path = input("Please input your .ia path: ")

    file = open(ia_path, "r")

    code = file.read()

    name = input("Please input project name: ")

    my_project = create_project_beta(code, cursor)

    scratchjr.set_project_json(cursor, name, my_project)
    print(json.dumps(my_project.get_object()))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
