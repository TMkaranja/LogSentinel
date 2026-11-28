# Qt / PySide6 licence notice inventory

Status: **collected for review**. This inventory records what was shipped, what was
collected, and what remains open. It is not a legal opinion and does not establish
licence compliance.

Packet audited: `dist/gui-ondir-test/LogSentinel-GUI/` (one-directory build,
executable `86517ebc…`, 185 files). Component versions were read from the shipped
binaries' own version resources and from the installed wheel metadata, not from
this document.

## 1. Shipped components and their licensing options

| # | Component | Version | Bundled at | Licence options | Official source | Notice file | Outstanding uncertainty |
|---|---|---|---|---|---|---|---|
| 1 | Qt Core / Gui / Widgets / Network | 6.12.0.0 | `_internal/PySide6/Qt6{Core,Gui,Widgets,Network}.dll` | LGPLv3 (primary); GPLv2 / GPLv3 / commercial alternatives | <https://doc.qt.io/qt-6/lgpl.html> | `qt-lgpl.html` | None specific; which alternative applies is an election, not a fact |
| 2 | Qt Svg | 6.12.0.0 | `_internal/PySide6/Qt6Svg.dll`, `plugins/imageformats/qsvg.dll`, `plugins/iconengines/qsvgicon.dll` | as above | <https://doc.qt.io/qt-6/lgpl.html> | `qt-lgpl.html` | none |
| 3 | Qt PDF | 6.140.0.0 | `_internal/PySide6/Qt6Pdf.dll`, `plugins/imageformats/qpdf.dll` | LGPLv3 **or GPLv2** or commercial | <https://doc.qt.io/qtpdf/qtpdf-licensing.html> | `qtpdf-licensing.html` | Embeds a PDFium snapshot; PDFium/Chromium/Abseil attributions not yet collected. Application never imports Qt PDF |
| 4 | Qt plugins (21) and translations (99 `.qm`) | 6.12.0.0 | `_internal/PySide6/plugins/…`, `_internal/PySide6/translations/` | LGPLv3 / commercial | <https://doc.qt.io/qt-6/lgpl.html> | `qt-lgpl.html` | Translation files may carry contributor copyrights not listed per-file |
| 5 | PySide6 bindings | 6.12.0 | `_internal/PySide6/{QtCore,QtGui,QtNetwork,QtSvg,QtWidgets}.pyd`, `pyside6.abi3.dll` | Wheel metadata: `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`. Docs: "Community Edition (LGPLv3/GPLv3)" plus commercial | <https://doc.qt.io/qtforpython-6/commercial/index.html> | `qtforpython-commercial.html`, `LicenseRef-Qt-Commercial.txt` | Docs and wheel metadata disagree on the GPLv2 option (see §4) |
| 6 | Shiboken6 | 6.12.0 | `_internal/shiboken6/Shiboken.pyd`, `_internal/shiboken6/shiboken6.abi3.dll` | Same statement as PySide6 ("Qt for Python follows the same licensing that Qt has"); wheel metadata identical | <https://doc.qt.io/qtforpython-6/commercial/index.html> | as row 5 | No Shiboken-specific notice page was found; treated under the Qt for Python statement. Needs vendor confirmation |
| 7 | PySide6_Pdf distribution (carries Qt PDF binaries) | 6.12.0.140 | indirectly: `Qt6Pdf.dll`, `qpdf.dll` | as row 3 | <https://doc.qt.io/qtpdf/qtpdf-licensing.html> | `qtpdf-licensing.html` | Version scheme differs from Qt (6.140.0 vs 6.12.0) because Qt PDF is released from the Qt WebEngine line |

## 2. Collected files (verbatim, as published)

| File | Bytes | SHA-256 | Source URL | Server `Content-Length` / `Last-Modified` |
|---|---:|---|---|---|
| `qt-lgpl.html` | 32,212 | `e78d1e67fb21d2cf0b20f0863bfc3518edac9774ec3aae8afab8ce050c410825` | <https://doc.qt.io/qt-6/lgpl.html> | 32212 / Wed, 30 Sep 2026 06:37:26 GMT |
| `qt-licensing.html` | 24,587 | `4e44ffea2f2a76d6a80d8d223b97fae88defcffa1c40e1a78ae418763c61a9f3` | <https://doc.qt.io/qt-6/licensing.html> | 24587 / Wed, 30 Sep 2026 06:37:26 GMT |
| `qtpdf-licensing.html` | 19,662 | `cd2289ee5522228200a5d396a39924672ca16dc471fa03309d2392b805997ea2` | <https://doc.qt.io/qtpdf/qtpdf-licensing.html> | 19662 / Fri, 13 Nov 2026 10:53:43 GMT |
| `qtforpython-commercial.html` | 356,213 | `2fe3b6af2041e62d7609fc7e42abab98f27aea2805e061f5777a9e2b69f21beb` | <https://doc.qt.io/qtforpython-6/commercial/index.html> | 356213 / Thu, 08 Oct 2026 15:44:05 GMT |
| `LicenseRef-Qt-Commercial.txt` | 470 | `4f54763ac0fe2abd8f7f8d8fe370a94a08ebf84786aa0b91045bd6628deb08a3` | shipped in `pyside6-6.12.0.dist-info/licenses/` (same file in `shiboken6` and `pyside6_pdf`) | n/a (local wheel artefact) |

Each HTML file was downloaded whole and stored unmodified; the notice sentences are
embedded in larger documents (the LGPL page also carries the full LGPL text, the
licensing page carries the GPLv3-only module list), so the complete documents were
preserved rather than excerpted.

## 3. Notice and licensing statements as published

- **Qt LGPL notice** (`qt-lgpl.html`): "The Qt Toolkit is Copyright (C) 2018 The Qt
  Company Ltd. and other contributors. Contact: <https://www.qt.io/licensing/>".
  Same page states: "Qt is available under the GNU Lesser General Public License
  version 3."
- **Module alternatives** (`qt-licensing.html`): "For open-source licensed Qt, some
  specific parts (modules) are not available under the GNU LGPL version 3, but under
  the GNU General Public License (GPL) instead", followed by the list of GPLv3-only
  modules (Canvas Painter, CoAP, Graphs, GRPC, HTTP Server, Lottie, MQTT, Network
  Authorization, Qml Compiler, Quick 3D, Quick 3D Physics, Quick Timeline, Virtual
  Keyboard, Wayland Compositor). None of those modules is present in this build.
- **Qt PDF** (`qtpdf-licensing.html`): "available under commercial licenses from The
  Qt Company. In addition, it is available under the GNU Lesser General Public
  License, version 3, or the GNU General Public License, version 2." The page also
  states the module "includes a snapshot of PDFium".
- **Qt for Python / PySide6 / Shiboken6** (`qtforpython-commercial.html`): "Qt for
  Python follows the same licensing that Qt has, which means that there are two
  distributions, the Community Edition (LGPLv3/GPLv3) and a Commercial Edition."
- **Wheel licence stub** (`LicenseRef-Qt-Commercial.txt`): a 470-byte pointer to
  commercial terms. It is the only licence file the PySide6, PySide6_Pdf and
  shiboken6 wheels ship; **no LGPL text is bundled in any wheel**.

## 4. Missing notices, ambiguity and open items

1. **GPL alternative discrepancy.** Wheel metadata declares
   `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only` for PySide6, PySide6_Pdf and
   shiboken6; the vendor documentation describes the community edition as
   "LGPLv3/GPLv3". Whether GPL-2.0-only is genuinely available for the bindings is
   unresolved and must be confirmed with The Qt Company. It does not affect an
   LGPLv3 election, but it must not be asserted either way in a release notice.
2. **No LGPL text in the wheels.** `licenses/LGPL-3.0.txt` (previously verified,
   SHA-256 `e3a994d8…5f23118`) supplies the licence text required by LGPLv3 §4(b);
   `licenses/GPL-3.0.txt` supplies the GPL text that LGPLv3 incorporates.
3. **Qt third-party attributions are not collected here.** Qt's per-module
   attribution list (`licenses-used-in-qt.html`) and the component texts it covers
   (FreeType, HarfBuzz, libpng, libjpeg-turbo, libtiff, libwebp, zlib, PCRE2,
   TinyCBOR, double-conversion, PDFium, Chromium, Abseil, Little CMS, ICU,
   fast_float, anti-grain geometry, libpsl, Public Suffix List, and the rest) belong
   to the next step of the inventory and must not be treated as satisfied.
4. **Qt PDF decision pending.** Qt PDF is LGPLv3/GPLv2 and is bundled but never
   imported by the application. Whether to keep shipping it is a product/release
   decision with a direct effect on the attribution and relinking surface.
5. **Shiboken6 notice basis.** No dedicated Shiboken6 license page was located;
   coverage rests on the Qt for Python statement plus wheel metadata. Confirm with
   the vendor if a separate notice is expected.
6. **Copyright years.** The published Qt notice says 2018; the documentation footer
   says 2026. The notice text was preserved as published rather than updated.
7. **No commercial licence is held.** All statements above describe the open-source
   alternatives only.

## 5. Completeness assessment

The Qt/PySide6 notice set is **complete enough to proceed** to the remaining
third-party inventory: the licence options, the required Qt notice, the LGPLv3-only
versus GPLv3-only module distinction, the Qt PDF variant, and the Qt for Python
statement are all captured from vendor-published documents with verifiable
provenance.

It is **not** complete for release. Rows 3, 5, 6 and items 1, 3 and 4 of §4 remain
open, and no conclusion about compliance should be drawn from this collection.
