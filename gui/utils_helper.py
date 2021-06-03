# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : helper.py
# ------------------------------------------------------------------------------
#
# File          : helper.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os, sys, platform, uuid, bitstring
import psutil
import wx
from application.define import APP_CONSOLE_TIME_WX_FMT


def util_get_ipv4_if():
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == -1:
                mac = snic.address
            if snic.family == 2:
                yield interface, snic.address, snic.netmask, mac


def util_is_32bit_pcap_installed():
    # todo: for linux and mac must be different
    _32_sys_path = os.environ['WINDIR'] + "\\System32\\"
    return os.path.exists(os.path.join(_32_sys_path, 'Packet.dll'))


def util_is_64bit_pcap_installed():
    # todo: for linux and mac must be different
    _64_sys_path = os.environ['WINDIR'] + "\\SysWOW64\\"
    return os.path.exists(os.path.join(_64_sys_path, 'Packet.dll'))


def util_os_is_32bit():
    return sys.maxsize <= 2 ** 32


def util_os_is_windows():
    return (bool(platform.win32_ver()[0]) or
            (sys.platform in ("win32", "cygwin")) or
            (sys.platform == "cli" and os.name in ("nt", "ce")) or
            (os.name == "java" and
             "windows" in platform.java_ver()[3][0].lower()))


def util_os_is_linux():
    return sys.platform.startswith("linux")


def util_os_is_osx():
    return sys.platform == "darwin"


def util_os_is_posix():
    return os.name == "posix"


def util_date_now(fmt=APP_CONSOLE_TIME_WX_FMT):
    return wx.DateTime.UNow().Format(fmt)


def util_get_segment_of_list(lst: list, seg: int):
    if seg > 0:
        return [lst[x:x + seg] for x in range(0, len(lst), seg)]
    else:
        return lst


def util_get_ascii_chr(val, char_rep='.'):
    return chr(val) if 127 >= val > 32 else char_rep


def util_get_formatted_hex_byte_str(val, char_w=0):
    return ('%.2X' % val).ljust(char_w)


def util_set_val_by_bit_rang(offset, bit_len, val, target):
    for i in range(bit_len):
        _c1 = (val & (1 << i))
        if _c1:
            target = util_set_bit(target, i + offset)
        else:
            target = util_clear_bit(target, i + offset)
    return target


def util_set_bits(offset, length, val):
    return (((pow(2, length) - 1) << offset) & val) >> offset


def util_set_bit(value, bit):
    return value | (1 << bit)


def util_clear_bit(value, bit):
    return value & ~(1 << bit)


def util_get_uuid_string():
    return uuid.uuid4().hex


def util_cvt_path_to_platform_spec(path):
    """
    Convert paths to the platform-specific separator
    """
    st = os.path.join(*tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st


def util_wx_tree_walk_branches(tree, root):
    """
    a generator that recursively yields child nodes of a wx.TreeCtrl
    """
    item, cookie = tree.GetFirstChild(root)
    while item.IsOk():
        yield item
        if tree.ItemHasChildren(item):
            util_wx_tree_walk_branches(tree, item)
        item, cookie = tree.GetNextChild(root, cookie)


def util_int2byte(x: int, endian='big') -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, endian)


def util_int2chars(x: int, endian='big') -> list:
    return [chr(x) for x in util_int2byte(x, endian)]


def util_int2string(x: int, endian='big', sep=',') -> str:
    return sep.join(util_int2chars(x, endian))


def util_chars2uint8s(chars):
    return [ord(x) for x in chars]


def util_uint82int(uint8s: list):
    _fmt = ','.join(['uint:8'] * len(uint8s))
    return bitstring.pack(_fmt, *uint8s).uint
