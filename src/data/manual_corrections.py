# handling edge cases before writing the finalized and tagged JSON
def hard_coded_corrections(sorted_dict):

    # multiple alternative (i.e., not summed) damage types and "invisible" catch
    sorted_dict["Glyph of Warding"]["tags"]["damage"]["base_damage"] = [
        {
            "damage_type": [
                type for type in ["acid", "cold", "fire", "lightning", "thunder"]
            ],
            "damage_average": 22.5,
            "damage_maximum": 40.0,
        }
    ]
    sorted_dict["Glyph of Warding"]["tags"]["conditions"] = []

    sorted_dict["Spirit Guardians"]["tags"]["damage"]["base_damage"] = [
        {
            "damage_type": [type for type in ["radiant", "necrotic"]],
            "damage_average": 22.5,
            "damage_maximum": 40.0,
        }
    ]

    sorted_dict["Chaos Bolt"]["tags"]["damage"]["base_damage"] = [
        {
            "damage_type": [
                [
                    type
                    for type in [
                        "acid",
                        "cold",
                        "fire",
                        "force",
                        "lightning",
                        "poison",
                        "psychic",
                        "thunder",
                    ]
                ]
            ],
            "damage_average": 12.5,
            "damage_maximum": 22.0,
        }
    ]

    sorted_dict["Chromatic Orb"]["tags"]["damage"]["base_damage"] = [
        {
            "damage_type": [
                [
                    type
                    for type in [
                        "acid",
                        "cold",
                        "fire",
                        "lightning",
                        "poison",
                        "thunder",
                    ]
                ]
            ],
            "damage_average": 13.5,
            "damage_maximum": 28.0,
        }
    ]

    # non-standard base damage calculation
    sorted_dict["Blade of Disaster"]["tags"]["damage"]["base_damage"] = [
        {"damage_type": "force", "damage_average": 52.0, "damage_maximum": 288.0},
    ]

    sorted_dict["Booming Blade"]["tags"]["damage"]["base_damage"] = [
        {"damage_type": "thunder", "damage_average": 4.5, "damage_maximum": 8.0},
    ]

    sorted_dict["Guardian of Faith"]["tags"]["damage"]["base_damage"] = [
        {"damage_type": "radiant", "damage_average": 20.0, "damage_maximum": 20.0},
    ]

    sorted_dict["Magic Missile"]["tags"]["damage"]["base_damage"] = [
        {"damage_type": "force", "damage_average": 10.5, "damage_maximum": 15.0}
    ]

    sorted_dict["Scorching Ray"]["tags"]["damage"]["base_damage"] = [
        {"damage_type": "fire", "damage_average": 21.0, "damage_maximum": 36.0}
    ]

    sorted_dict["Spiritual Weapon"]["tags"]["damage"]["base_damage"] = [
        {"damage_type": "force", "damage_average": 4.5, "damage_maximum": 8.0},
    ]

    # AOE shapes and sizes
    sorted_dict["Blade Barrier"]["tags"]["aoe"] = [
        {"aoe_size": 100.0, "aoe_shape": "line"},
        {"aoe_size": 60.0, "aoe_shape": "sphere"},
    ]

    sorted_dict["Tsunami"]["tags"]["aoe"] = [
        {"aoe_size": 300.0, "aoe_shape": "line"},
    ]

    sorted_dict["Wall of Fire"]["tags"]["aoe"] = (
        {"aoe_size": 60.0, "aoe_shape": "line"},
        {"aoe_size": 20.0, "aoe_shape": "sphere"},
    )

    sorted_dict["Wall of Force"]["tags"]["aoe"] = [
        {"aoe_size": 20.0, "aoe_shape": "sphere"},
        {"aoe_size": 100.0, "aoe_shape": "line"},
    ]

    sorted_dict["Wall of Ice"]["tags"]["aoe"] = [
        {"aoe_size": 20.0, "aoe_shape": "sphere"},
        {"aoe_size": 100.0, "aoe_shape": "line"},
    ]

    sorted_dict["Wall of Light"]["tags"]["aoe"] = [
        {"aoe_size": 60.0, "aoe_shape": "line"},
    ]

    sorted_dict["Wall of Stone"]["tags"]["aoe"] = [
        {"aoe_size": 200.0, "aoe_shape": "line"},
    ]

    sorted_dict["Wall of Thorns"]["tags"]["aoe"] = [
        {"aoe_size": 60.0, "aoe_shape": "line"},
        {"aoe_size": 20.0, "aoe_shape": "sphere"},
    ]

    sorted_dict["Wall of Water"]["tags"]["aoe"] = [
        {"aoe_size": 30.0, "aoe_shape": "line"},
        {"aoe_size": 20.0, "aoe_shape": "sphere"},
    ]
