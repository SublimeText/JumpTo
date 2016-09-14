I'm not actively working on this project anymore. If somebody wants to maintain it, please send me an email to jonas.pfannschmidt at gmail.com. Otherwise, https://github.com/xavi-/sublime-selectuntil seems to be a good alternative.

Summary
=======

JumpTo is a plugin for Sublime Text 2 to move the cursor to any position in the current line. It's very similar to some movement commands in Vim. This is especially useful when editing multiple similar lines at the same time.

Watch [this video](http://vimeo.com/48392058) to see a real world example on how I use it to refactore some code.

Install
=======

- Copy this repository into the Sublime Text 2 "Packages" directory.
- Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)

Usage
=====

Press ctrl+e (or click on Goto -> Jump to) and enter a search string. The cursor will jump to the start of the first occurence of this search string.

Press ctrl+shift+e (or click on Selection -> Expand Selection to) to select all characters from the current cursor position to the first occurence of the search string.

License
=======

Copyright (c) 2012, Jonas Pfannschmidt

Licensed under the MIT license http://www.opensource.org/licenses/mit-license.php
