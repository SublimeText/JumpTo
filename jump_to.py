"""
Copyright (c) 2012, Jonas Pfannschmidt
Contributors:
    - Dominique Wahli
Licensed under the MIT license http://www.opensource.org/licenses/mit-license.php
"""
import sublime
import sublime_plugin


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

    def process_regions(self):
        sel = self.view.sel()
        localedit = self.view.begin_edit()
        for reg, new_reg in self.regions:
            if new_reg is not None:
                sel.subtract(reg)
                sel.add(new_reg)
        self.view.end_edit(localedit)
        self.regions = []

    def select_regions(self, characters):
        sel = self.view.sel()
        self.regions = []
        for reg in sel:
            new_pt = self.find_next(characters, reg.b)
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


ADDREGIONS_SCOPE = "comment"
ADDREGIONS_FLAGS = sublime.DRAW_EMPTY | sublime.DRAW_OUTLINED


class JumpToInteractiveCommand(JumpToBase, sublime_plugin.WindowCommand):
    def run(self, characters="", extend=False):
        self._run(None, self.window.active_view(), extend)
        text = "Expand selection to:" if extend else "Jump to:"
        self.window.show_input_panel(text, characters, self._on_enter, self._on_change, self._on_cancel)

    def _remove_highlight(self):
        self.regions = []
        self.view.erase_regions("JumpTo")

    def _show_highlight(self):
        if self.regions:
            regions = [(r[1] if r[1] is not None else r[0]) for r in self.regions]
            self.view.add_regions("JumpTo", regions, ADDREGIONS_SCOPE, ADDREGIONS_FLAGS)

    def _on_enter(self, characters):
        self._remove_highlight()
        # Have to execute select_regions for the case when:
        # - the input_panel is open and you type something
        # - the user use the mouse to change the cursor(s) position
        # - he return to the input_panel and hit enter
        # In this case _on_change is not executed.
        # self.select_regions(characters)
        # self.process_regions()
        # Finally, why not simply run the command ? This way the undo label is correct and it works with macro.
        self.view.run_command("jump_to", {"characters": characters, "extend": self.extend})

    def _on_change(self, characters):
        self.select_regions(characters)
        self._show_highlight()

    def _on_cancel(self):
        self._remove_highlight()
