### [unreleased]
## Added
- this file - CHANGELOG.md
- myinputdata.py class to (de) serialize each input line
- Ctrl+Shift+R stops recording by raising event!
- Run prints actions to console
- run options! Edit -> Options and prompted on open
- commit messaged add #xx to link to isssue and prefix w/ 'close' to close - merge to master?!
- export!
## Changed
- refactored following pylint
- pymybase located in packages module
- pymybase only included needed files (not entire repo!)
- refactored app components and follow cookiecutter
- press and time in script precision 4 decimals
## Bug
- MySettingsDialog not capture all (can still drap root and get's shortcuts???
## Fixed
- no keyboard long hold due to keyboard - increase C/S override caused issues
## Removed