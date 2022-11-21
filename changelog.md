# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic 
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

- `qtconsole.rich_ipython_widget` -> `qtconsole.rich_jupyter_widget` due to 
  deprecation

- PIT now uses `utilities.make_slice()` with the `silent=True` option to suppress 
  a warning.
  
- `from matplotlib.pyplot import colormaps` changed to 
  `from matplotlib.pyplot import get_cmap` to align with matplotlib change.

### Deprecated

### Removed

### Fixed

## [1.0.3] = 2022-10-24

### Changed

- `qtconsole.rich_ipython_widget` -> `qtconsole.rich_jupyter_widget` due to 
  deprecation

- PIT now uses `utilities.make_slice()` with the `silent=True` option to suppress 
  a warning.

## [1.0.2] = 2022-10-19

### Changed

- :class:`cmaps.ds_cmap` is now just an empty shell, in order to fix a bug. 
  In turn, alpha and gamma sliders don't work anymore. The original code is 
  retained in :class:`cmaps.ds_cmaps_legacy`.

- Created compatibility for PyQt5 by exchanging many instances of `QtGui` 
  with `QtWidgets`.

### Fixed

- ImageItems and GLImageItems not showing up due to a change of how colormaps 
  work in pyqtgraph.

## [1.0.1] - 2022-10-19

### Added

- changelog.md
