Summary
=======

JumpTo is a plugin for Sublime Text
to move the cursor to any position in the current line.
It's very similar to some movement commands in Vim.
This is especially useful
when editing multiple similar lines at the same time
with multiple selections.

Watch [this video](http://vimeo.com/48392058)
to see a real world example
on how I use it to refactor some code.

Install
=======

1. [Install Package Control](https://packagecontrol.io/installation).
1. In the Command Palette, select <kbd>Package Control: Install Package</kbd>.
1. Select `JumpTo`.
1. Create keymaps for the commands 
   (see `Example.sublime-keymap` for a suggestion).

Usage
=====

The package does not define key bindings by default,
so you must add them on your own.

With the bindings shown in `Example.sublime-keymap`,
you can use it like follows:

- Press <kdb>ctrl+e</kdb>
  (or select on Goto -> Jump to)
  and enter a search string.
  The cursor will jump to the start
  of the first occurrence of this search string.

- Press <kbd>ctrl+shift+e</kbd>
  (or select on <kbd>Selection -> Expand Selection to …<kbd>)
  to select all characters from the current cursor position
  to the first occurrence of the search string.

Options
========

- `extend`:
  Extend the current selection until the search result.
- `create_new`:
  Whether the current caret(s) should stay
  and a new caret should be created at the target position.
- `whole_match`:
  Whether the command should result in a selection from the matched text
  instead of a single caret at the start of the match.

License
=======

Copyright (c) 2012, Jonas Pfannschmidt

Licensed under the MIT license http://www.opensource.org/licenses/mit-license.php
