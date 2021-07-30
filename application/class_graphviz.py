# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_graphviz.py
# ------------------------------------------------------------------------------
#
# File          : class_graphviz.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import platform, subprocess, typing, os
import errno
from .utils_helper import *


class Graphviz:
    ENGINES = {  # http://www.graphviz.org/pdf/dot.1.pdf
        'dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp', 'patchwork', 'osage',
    }

    FORMATS = {  # http://www.graphviz.org/doc/info/output.html
        'bmp',
        'canon', 'dot', 'gv', 'xdot', 'xdot1.2', 'xdot1.4',
        'cgimage',
        'cmap',
        'eps',
        'exr',
        'fig',
        'gd', 'gd2',
        'gif',
        'gtk',
        'ico',
        'imap', 'cmapx',
        'imap_np', 'cmapx_np',
        'ismap',
        'jp2',
        'jpg', 'jpeg', 'jpe',
        'json', 'json0', 'dot_json', 'xdot_json',  # Graphviz 2.40
        'pct', 'pict',
        'pdf',
        'pic',
        'plain', 'plain-ext',
        'png',
        'pov',
        'ps',
        'ps2',
        'psd',
        'sgi',
        'svg', 'svgz',
        'tga',
        'tif', 'tiff',
        'tk',
        'vml', 'vmlz',
        'vrml',
        'wbmp',
        'webp',
        'xlib',
        'x11',
    }

    RENDERERS = {  # $ dot -T:
        'cairo',
        'dot',
        'fig',
        'gd',
        'gdiplus',
        'map',
        'pic',
        'pov',
        'ps',
        'svg',
        'tk',
        'vml',
        'vrml',
        'xdot',
    }

    FORMATTERS = {'cairo', 'core', 'gd', 'gdiplus', 'gdwbmp', 'xlib'}

    ENCODING = 'utf-8'

    PLATFORM = platform.system().lower()

    def __init__(self, graphviz_bin_path, image_path):
        self._binPath = graphviz_bin_path
        self._imagePath = image_path

    def get_startupinfo(self):
        if self.PLATFORM == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        else:
            return None

    def _build_command(self, engine: str, format_: str):
        """Return args list for ``subprocess.Popen`` and name of the rendered file."""

        if engine not in self.ENGINES:
            raise ValueError(f'unknown engine: {engine!r}')
        if format_ not in self.FORMATS:
            raise ValueError(f'unknown format: {format_!r}')

        _output_format = [f for f in (format_,) if f is not None]
        # cmd = ['dot', '-K%s' % engine, '-T%s' % ':'.join(output_format)]
        _cmd = [os.path.join(self._binPath, 'dot.exe'), '-K%s' % engine, '-T%s' % ':'.join(_output_format)]

        return _cmd

    def _execute(self, cmd, input, encoding='utf-8', **kwargs):
        if input is not None:
            kwargs['stdin'] = subprocess.PIPE
            if encoding is not None:
                input = input.encode(encoding)
        try:
            _proc = subprocess.Popen(cmd, startupinfo=self.get_startupinfo(), **kwargs)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise IOError('Executable dot not found: %s' % e)
            else:
                raise
        _out, _err = _proc.communicate(input)
        if encoding is not None:
            if _out is not None:
                _out = _out.decode(encoding)
            if _err is not None:
                _err = _err.decode(encoding)
        return _out, _err

    def render_dot_string_to_file(self, dot_str, path=None):
        if path is None:
            path = self._imagePath
        if not util_is_dir_exist(path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write('')
        _cmd = self._build_command('dot', 'png')
        with open(path, 'wb') as f:
            _out, _err = self._execute(_cmd, dot_str, encoding='utf-8', stdout=f)
        return path
