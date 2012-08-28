"""
Copyright (c) 2012, Jonas Pfannschmidt
Licensed under the MIT license http://www.opensource.org/licenses/mit-license.php
"""
import re
import sublime, sublime_plugin

class JumpTo(sublime_plugin.TextCommand):
    def find_next(self, char, pt):
        lr = self.view.line(pt)
        line = self.view.substr(sublime.Region(pt, lr.b))
        idx = line.find(char, 1)

        if idx >= 0:
            return pt + idx
        else:
            return False

    def run(self, edit, select = False):
        self.select = select
        text = "Expand selection to:" if select else "Jump to:"

        self.view.window().show_input_panel(text, "", self.on_enter, None, None)

    def on_enter(self, character):
        sel = self.view.sel()

        for reg in sel:
            new_pt = self.find_next(character, reg.b)

            if new_pt:
                if self.select:
                    new_reg = sublime.Region(reg.a, new_pt)
                else:
                    new_reg = sublime.Region(new_pt, new_pt)

                sel.subtract(reg)
                sel.add(new_reg)

                self.view.show(new_pt)

