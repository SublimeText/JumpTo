"""
Copyright (c) 2012, Jonas Pfannschmidt
Contributors:
    - Dominique Wahli
    - Xavi (https://github.com/xavi-/sublime-selectuntil)
Licensed under the MIT license http://www.opensource.org/licenses/mit-license.php
"""
import sublime
import sublime_plugin
import re

RE_SELECTOR = re.compile("^(?:\{(-?\d+)\}|\[(.+)\]|/(.+)/)$")


class JumpToBase(object):
    def _run(self, edit, view, extend=False):
        self.extend = extend
        self.regions = []
        if view:
            self.view = view

    def find_next(self, chars, pt):
        if chars == "":
            return False

        lr = self.view.line(pt)
        line = self.view.substr(sublime.Region(pt, lr.b))
        idx = line.find(chars, 1)

        if idx >= 0:
            return pt + idx
        else:
            return False

    def find_next_re(self, chars, pt):
        if chars == "":
            return False

        lr = self.view.line(pt)
        line = self.view.substr(sublime.Region(pt, lr.b))
        try:
            result = re.search(chars, line)
        except:
            sublime.status_message("JumpTo: Error in regex !")
            return False

        if result is not None:
            idx = result.start()
            return pt + idx
        else:
            return False

    def find_next_count(self, count, pt):
        if count <= 0:
            return False

        lr = self.view.line(pt)
        idx = pt + count

        if idx <= lr.b:
            return idx
        else:
            return False

    def process_regions(self):
        sel = self.view.sel()
        for reg, new_reg in self.regions:
            if new_reg is not None:
                sel.subtract(reg)
                sel.add(new_reg)
        self.regions = []

    def select_regions(self, characters):
        result = RE_SELECTOR.search(characters)
        if result:
            groups = result.groups()
            count = int(groups[0]) if groups[0] is not None else None
            chars = groups[1]
            regex = groups[2]
        else:
            count = None
            chars = characters
            regex = None

        sel = self.view.sel()
        self.regions = []
        for reg in sel:
            if chars:
                new_pt = self.find_next(chars, reg.b)
            elif regex:
                new_pt = self.find_next_re(regex, reg.b)
            elif count:
                new_pt = self.find_next_count(count, reg.b)
            else:
                new_pt = False
            if new_pt is not False:
                if self.extend:
                    new_reg = sublime.Region(reg.a, new_pt)
                else:
                    new_reg = sublime.Region(new_pt, new_pt)
            else:
                new_reg = None
            self.regions.append((reg, new_reg))


class JumpToCommand(JumpToBase, sublime_plugin.TextCommand):
    def run(self, edit, characters="", extend=False):
        self._run(edit, None, extend)
        self.select_regions(characters)
        self.process_regions()


ADDREGIONS_SCOPE = "jumpto"
ADDREGIONS_FLAGS = sublime.DRAW_EMPTY | sublime.DRAW_OUTLINED


class JumpToInteractiveCommand(JumpToBase, sublime_plugin.WindowCommand):
    def run(self, characters="", extend=False):
        self._run(None, self.window.active_view(), extend)
        text = "Expand selection" if extend else "Jump"
        text += " to (chars or [chars] or {count} or /regex/):"
        self.window.show_input_panel(text, characters, self._on_enter, self._on_change, self._on_cancel)

    def _remove_highlight(self):
        self.regions = []
        self.view.erase_regions("JumpTo")

    def _show_highlight(self):
        if self.regions:
            regions = [(r[1] if r[1] is not None else r[0]) for r in self.regions]
            self.view.add_regions("JumpTo", regions, ADDREGIONS_SCOPE, "", ADDREGIONS_FLAGS)

    def _on_enter(self, characters):
        self._remove_highlight()
        # Could not simply use process_regions() for the case when:
        # - the input_panel is open and you type something
        # - the user use the mouse to change the cursor(s) position
        # - he return to the input_panel and hit enter
        # In this case _on_change is not executed.
        # So we simply run the command.
        # This way the undo label is correct and it works with macro.
        self.view.run_command("jump_to", {"characters": characters, "extend": self.extend})

    def _on_change(self, characters):
        self.select_regions(characters)
        self._show_highlight()

    def _on_cancel(self):
        self._remove_highlight()
