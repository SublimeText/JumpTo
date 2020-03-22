import sublime
import sublime_plugin
import re


def find_next_literal(view, pt, arg):
    lr = view.line(pt)
    line = view.substr(sublime.Region(pt, lr.b))
    idx = line.find(arg)

    if idx != -1:
        pt_start = pt + idx
        return sublime.Region(pt_start, pt_start + len(arg))


def find_next_re(view, pt, arg):
    lr = view.line(pt)
    line = view.substr(sublime.Region(pt, lr.b))
    try:
        result = re.search(arg, line)
    except Exception:
        sublime.status_message("JumpTo: Error in regular expression!")
        return

    if result:
        return sublime.Region(pt + result.start(), pt + result.end())


def find_next_count(view, pt, arg):
    lr = view.line(pt)
    idx = pt + int(arg)
    if lr.a <= idx <= lr.b:
        return sublime.Region(idx, idx)


MATCHERS = [
    (r"\[(.+)\]", find_next_literal),
    (r"/(.+)/", find_next_re),
    (r"\{(-?\d+)\}", find_next_count),
]


def find_regions(view, start_regions, text):
    find_func, arg = find_next_literal, text
    for pattern, func in MATCHERS:
        m = re.match(pattern, text)
        if m:
            find_func, arg = func, m.group(1)
            break

    for reg in start_regions:
        new_reg = find_func(view, reg.b, arg)
        yield reg, new_reg


def process_results(regions, whole_match, extend):
    for reg, new_reg in regions:
        if new_reg is None:
            yield reg
            continue
        if not whole_match:
            new_reg = sublime.Region(new_reg.a, new_reg.a)
        if extend:
            new_reg = sublime.Region(reg.a, new_reg.b)
        yield new_reg


def get_new_regions(view, text, whole_match, extend, **_):
    start_regions = list(view.sel())
    find_results = find_regions(view, start_regions, text)
    return process_results(find_results, whole_match, extend)


class JumpToCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, extend=False, create_new=False, whole_match=False):
        new_regions = get_new_regions(self.view, text, whole_match, extend)
        selection = self.view.sel()
        if not create_new:
            selection.clear()
        selection.add_all(new_regions)


class JumpToInteractiveCommand(sublime_plugin.WindowCommand):
    ADDREGIONS_KEY = "JumpTo"
    ADDREGIONS_SCOPE = "jumpto"
    ADDREGIONS_FLAGS = sublime.DRAW_EMPTY | sublime.DRAW_OUTLINED

    def run(self, text="", extend=False, create_new=False, whole_match=False):
        self.params = {'extend': extend, 'create_new': create_new, 'whole_match': whole_match}
        self.view = self.window.active_view()

        if extend:
            prompt = "Expand selection to"
        elif create_new:
            prompt = "Create caret at"
        else:
            prompt = "Jump to"
        prompt += " (chars or [chars] or {count} or /regex/):"

        self.window.show_input_panel(prompt, text, self._on_done, self._on_change, self._on_cancel)

    def _show_highlight(self, regions):
        if not regions:
            self.view.erase_regions(self.ADDREGIONS_KEY)
        else:
            self.view.add_regions(self.ADDREGIONS_KEY, regions,
                                  self.ADDREGIONS_SCOPE, "", self.ADDREGIONS_FLAGS)

    def _on_done(self, text):
        self._show_highlight(None)
        # Run the command to create a proper undo point
        args = self.params.copy()
        args['text'] = text
        self.view.run_command("jump_to", args)

    def _on_change(self, text):
        regions = list(get_new_regions(self.view, text, **self.params))
        if self.params['create_new']:
            regions += list(self.view.sel())
        self._show_highlight(tuple(regions))

    def _on_cancel(self):
        self._show_highlight(None)
