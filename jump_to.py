"""
Copyright (c) 2012, Jonas Pfannschmidt
Contributors:
    - Dominique Wahli
    - Xavi (https://github.com/xavi-/sublime-selectuntil)
    - Richard Stein
Licensed under the MIT license http://www.opensource.org/licenses/mit-license.php
"""
import sublime
import sublime_plugin
import re

RE_SELECTOR = re.compile(r"^(?:\{(-?\d+)\}|\[(.+)\]|/(.+)/)$")


class JumpToBase(object):
    def _run(self, edit, view, extend, create_new, whole_selection):
        self.extend = extend
        self.create_new = create_new
        self.whole_selection = whole_selection
        self.regions = []
        if view:
            self.view = view

    def find_next(self, chars, pt):
        if not chars:
            return

        lr = self.view.line(pt)
        line = self.view.substr(sublime.Region(pt, lr.b))
        idx = line.find(chars, 1)

        if idx >= 0:
            pt_start = pt + idx
            return sublime.Region(pt_start, pt_start + len(chars))

    def find_next_re(self, chars, pt):
        if not chars:
            return

        lr = self.view.line(pt)
        line = self.view.substr(sublime.Region(pt, lr.b))
        try:
            result = re.search(chars, line)
        except Exception:
            sublime.status_message("JumpTo: Error in regex !")
            return

        if result:
            return sublime.Region(pt + result.start(), pt + result.end())

    def find_next_count(self, count, pt):
        if count <= 0:
            return

        lr = self.view.line(pt)
        idx = pt + count

        if idx <= lr.b:
            return sublime.Region(idx, idx)

    def process_regions(self):
        sel = self.view.sel()
        for reg, new_reg in self.regions:
            if new_reg is not None:
                if not self.create_new:
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
            count = regex = None
            chars = characters

        sel = self.view.sel()
        self.regions = []
        for reg in sel:
            if chars:
                new_reg = self.find_next(chars, reg.b)
            elif regex:
                new_reg = self.find_next_re(regex, reg.b)
            elif count:
                new_reg = self.find_next_count(count, reg.b)
            else:
                new_reg = None
            if new_reg is not None:
                if self.extend:
                    end = new_reg.b if self.whole_selection else new_reg.a
                    new_reg = sublime.Region(reg.a, end)
                elif not self.whole_selection:
                    new_reg = sublime.Region(new_reg.a, new_reg.a)
            self.regions.append((reg, new_reg))


class JumpToCommand(JumpToBase, sublime_plugin.TextCommand):
    def run(self, edit, characters="", extend=False, create_new=False,
            whole_selection=False):
        self._run(edit, None, extend, create_new, whole_selection)
        self.select_regions(characters)
        self.process_regions()


ADDREGIONS_SCOPE = "jumpto"
ADDREGIONS_FLAGS = sublime.DRAW_EMPTY | sublime.DRAW_OUTLINED


class JumpToInteractiveCommand(JumpToBase, sublime_plugin.WindowCommand):
    def run(self, characters="", extend=False, create_new=False,
            whole_selection=False):
        self._run(None, self.window.active_view(), extend, create_new,
                  whole_selection)
        if extend:
            text = "Expand selection to"
        elif create_new:
            text = "Create caret at"
        else:
            text = "Jump to"
        text += " (chars or [chars] or {count} or /regex/):"
        self.window.show_input_panel(text, characters, self._on_enter,
                                     self._on_change, self._on_cancel)

    def _remove_highlight(self):
        self.regions = []
        self.view.erase_regions("JumpTo")

    def _show_highlight(self):
        if not self.regions:
            return
        if self.create_new:
            regions = [r[0] for r in self.regions]
            regions.extend(r[1] for r in self.regions if r[1] is not None)
        else:
            regions = [(r[1] if r[1] is not None else r[0])
                       for r in self.regions]
        self.view.add_regions("JumpTo", regions, ADDREGIONS_SCOPE, "",
                              ADDREGIONS_FLAGS)

    def _on_enter(self, characters):
        self._remove_highlight()
        # Could not simply use process_regions() for the case when:
        # - the input_panel is open and you type something
        # - the user use the mouse to change the cursor(s) position
        # - he return to the input_panel and hit enter
        # In this case _on_change is not executed.
        # So we simply run the command.
        # This way the undo label is correct and it works with macro.
        self.view.run_command("jump_to",
                              {"characters": characters,
                               "extend": self.extend,
                               "create_new": self.create_new,
                               "whole_selection": self.whole_selection})

    def _on_change(self, characters):
        self.select_regions(characters)
        self._show_highlight()

    def _on_cancel(self):
        self._remove_highlight()
