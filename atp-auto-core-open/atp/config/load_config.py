# -*- coding:utf-8 -*-


def load_config(mode):
    try:
        if mode == "DEV":
            from atp.config.dev import DevConfig
            return DevConfig
        elif mode == "ALIUAT":
            from atp.config.aliuat import AliuatConfig
            return AliuatConfig
        else:
            raise ValueError("ENV MODE selection out of range")
    except ValueError as e:
        from atp.config.dev import DevConfig
        return DevConfig
