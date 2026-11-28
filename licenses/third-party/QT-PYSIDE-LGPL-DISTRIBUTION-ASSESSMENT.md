# Qt / PySide LGPL distribution assessment — trimmed Windows onedir package

**Assessment date:** 2026-11-09  
**Disposition:** **OPEN — NOT CLEARED FOR DISTRIBUTION.** This is a focused engineering evidence assessment, not legal advice, a legal opinion, or a compliance determination. It records package facts, public upstream statements, conditional license analysis, and unresolved questions. No license election or permission is inferred from a version string, signature, package metadata, or technical test alone.

## 1. Scope and question

This assessment considers the actual trimmed LogSentinel Windows GUI onedir package identified below and asks what would need to be established if Qt/PySide components in it are conveyed under the LGPL version 3. It is not a full third-party audit; see `FINAL-LICENSING-AUDIT.md` and `TRIMMED-PACKAGE-NOTICE-MAP.md` for the broader inventory and separate OpenSSL, PyInstaller, CPython, and Microsoft runtime questions.

The LGPL discussion is conditional. The package's exact Qt/PySide licensing basis and the distributor's selected licensing route have not been established. Public Qt statements, PyPI metadata and license expressions describe available terms; they do not prove which grant applies to these specific binaries or that any required distribution conditions have been met.

## 2. Artifact examined

- **Package:** `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- **Layout:** onedir; the executable is outside `_internal/`, and Qt/PySide runtime files are within it.
- **Inventory:** 182 regular files; 80,058,228 bytes total.
- **Executable:** `LogSentinel-GUI.exe`, 2,386,859 bytes; SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- **Types:** 42 DLLs, 16 PYDs, 99 Qt `.qm` translations, 22 SVGs, one ZIP, one ICO, and one EXE.
- **Qt modules observed:** Qt 6.12.0 `Qt6Core.dll`, `Qt6Gui.dll`, `Qt6Network.dll`, `Qt6Svg.dll`, and `Qt6Widgets.dll`; associated PySide6 extension modules and `pyside6.abi3.dll`; Shiboken components; Qt plugins including image-format and platform plugins; and the translation catalogs.
- **Exclusions observed:** `Qt6Pdf.dll`, `plugins/imageformats/qpdf.dll`, and `opengl32sw.dll` are absent. This statement is specific to this inventory, not to other builds.
- **Notices:** no `.txt`, `.md`, or `.rst` license/notice document is present in the package. The repository has license and evidence files, but their presence in the repository is not delivery with the package.

The count, byte total, type counts, absence of those notice-text suffixes, and executable hash were independently rechecked while preparing this assessment. They agree with the recorded baseline. The check did not replace or execute any packaged library.

## 3. What public license materials establish — and do not establish

### 3.1 Qt libraries and plugins

Qt's versioned licensing documentation says Qt is available under commercial licenses and, for eligible components, LGPL version 3 or GPL version 3; it also warns that some open-source Qt modules are GPL-only. The modules observed here are Core, Gui, Network, Svg, and Widgets, not the GPLv3-only module list reproduced in the prior Qt inventory. Qt's general statement is not a binary-specific license election or source-to-build attestation.

The `qt-licensing.html` and `qt-lgpl.html` collected in `licenses/third-party/qt/` are vendor documentation. They are useful evidence of published terms and notices; they do not establish that the shipped Windows wheel binaries are from a specific source revision, build configuration, license election, or commercial entitlement. Nor do they substitute for required end-user notices in this package.

### 3.2 PySide6 and Shiboken

The public PyPI page for PySide6 6.12.0 and the wheel metadata report the expression `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`. Qt for Python's commercial-use page describes the Community Edition as “LGPLv3/GPLv3” and describes separate commercial packages. These public statements do not line up perfectly on the GPLv2 alternative. The project must not silently resolve that difference: obtain written confirmation from Qt for the exact PySide6 and Shiboken6 distributions and binaries used, including their applicable alternatives and third-party notices.

The build provenance of the package's PySide6 and Shiboken files has not been tied here to exact wheel filenames and hashes, wheel source, source revisions, build flags, patches, or an applicable license election. Metadata is a useful lead, not proof of provenance or permission. A commercial license is not evidenced by this assessment.

Qt for Python also publishes a separate third-party license listing for code in Qt for Python/Shiboken. That scope is distinct from Qt's own module attribution list. The exact embedded third-party portions and notices for these binaries remain to be mapped.

### 3.3 Qt translations are a distinct scope

The package contains 99 `.qm` catalogs. Qt Project's active [QUIP 18](https://contribute.qt-project.org/quips/18/) classifies usual `translations/*.ts` files as `LicenseRef-Qt-Commercial OR BSD-3-Clause`. Qt documentation identifies translation catalogs as a separate `qttranslations` project and cautions that community-provided translations may be incorrect and should be audited. Thus the catalogs must not simply be described as LGPL Qt libraries or assumed covered by a Qt LGPL election. The exact `.qm`-to-source catalog mapping, relevant contributor notices, transformations and the correct BSD attribution materials for the shipped files have not been verified. The upstream classification is guidance for source files; it is not by itself a binary provenance record for these 99 compiled files.

### 3.4 Third-party code inside Qt/PySide

Qt modules and plugins can include third-party code under their own terms, including code linked into a Qt DLL or plugin. Qt's versioned attribution pages and SBOM materials are relevant evidence, but the report does not have a matching SBOM/build record for these Windows wheel binaries. The existing trimmed-package audit identifies candidate bundled material such as FreeType, HarfBuzz, libpng, PCRE2/SLJIT, libjpeg-turbo, libtiff, libwebp, C++/WinRT and zlib-compatible code. Several exact revisions, choices between alternative licenses, source mappings, and full notice scopes remain unresolved. These third-party terms are not replaced by satisfying Qt's LGPL conditions; the broader audit's component-specific gaps remain release gates.

## 4. Conditional LGPLv3 distribution requirements

This section summarizes the relevant structure of LGPLv3 §4 for a combined work, for engineering planning only. The exact application, license scope, conveyance mode and obligations should be determined by qualified counsel against the final artifact and distribution model.

If the distributor relies on LGPLv3 for covered Qt/PySide libraries in a combined work, §4 includes, among other things:

1. **Prominent notice with each copy** that the Library is used and the Library and its use are covered by the LGPL.
2. **License texts:** accompany the combined work with copies of the GNU GPL and LGPL license documents. The LGPLv3 text incorporates GPLv3 terms; the repository has `licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt`, but this package contains neither.
3. **Runtime copyright notices where applicable:** if the combined work displays copyright notices during execution, include the Library's copyright notice among them and refer users to the license copies.
4. **One of the §4(d) routes:**
   - **§4(d)(0), source / relinking route:** convey the Minimal Corresponding Source under the LGPL and Corresponding Application Code in a form and under terms permitting the user to recombine or relink the Application with a modified version of the Linked Version to make a modified combined work, using the GPLv3 §6 conveyance method; or
   - **§4(d)(1), shared-library route:** use a suitable shared-library mechanism that uses a copy of the Library already present on the user's system and operates properly with an interface-compatible modified version of the Linked Version.
5. **No effective restrictions:** the combined-work terms must not effectively restrict modification of the Library portions or reverse engineering for debugging those modifications.
6. **Installation Information, if triggered:** §4(e) requires it only where it would otherwise be required under GPLv3 §6, and only to the extent needed to install and execute the modified combined work. Whether this applies depends on facts about the device, conveyance and technical restrictions; it is not resolved for this package.

Qt's own [LGPL obligations guidance](https://www.qt.io/development/open-source-lgpl-obligations) recommends delivering complete corresponding source for the LGPL library, including modifications, or providing an offer with instructions to obtain it, and stresses preserving end-user freedoms. Apply the actual license text and chosen conveyance route; do not treat the vendor summary as a replacement for the license or legal review. In particular, this assessment does not prescribe a generic written-offer term or conclude which GPLv3 §6 method applies.

## 5. Replaceability, relinking and this onedir build

### What the layout supports

The onedir arrangement keeps Qt DLLs as separate files rather than embedding the whole runtime in a single-file executable. This is materially more inspectable and appears more amenable to replacing a shared library than a monolithic bundle. The Qt libraries are placed under `_internal/PySide6/`, with plugin directories alongside the runtime. That is a **layout observation only**.

### What has not been demonstrated for this exact artifact

- No recipient-controlled replacement test has been run against the verified `dist/gui-ondir-trim-test/LogSentinel-GUI/` directory in this assessment.
- A prior single-Qt-DLL replacement demonstration concerned another package/test arrangement and is explicitly not evidence that this exact trimmed artifact satisfies §4(d)(1).
- The package's Python extension modules (`.pyd`), `pyside6.abi3.dll`, Shiboken libraries, Qt DLLs, platform plugins, image plugins and related runtime files form an interdependent set. Replacing one Qt DLL is not proof a coherent interface-compatible replacement set can be loaded and run.
- The relevant loader search paths, PyInstaller runtime behavior, plugin discovery, dependency versions and replacement behavior on a recipient-controlled Windows system have not been validated for this exact build.
- No source-plus-application-code bundle and reproducible relinking/recombination procedure has been assembled or tested for §4(d)(0).
- The intended installer, update/signing policy, file permissions, end-user license/EULA, anti-tamper or other technical/legal restrictions are not specified here. No conclusion is made about reverse-engineering restrictions, replacement rights, or installation-information duties.

Accordingly, **neither §4(d) route is demonstrated**. The onedir layout is a useful starting point, not proof of legal sufficiency. A replacement probe must use a recipient-controlled copy of this exact package, a clearly identified interface-compatible replacement build (or a complete coherent set), and documented launch, UI, plugin and shutdown tests. Record the precise files and hashes before and after; do not overwrite or alter the preserved audit baseline without explicit release authorization. Technical success would still not decide legal sufficiency.

## 6. Source and relinking evidence required

A release source package or offer must match what was actually shipped, not merely a same-version public archive. Obtain and preserve, as relevant:

- exact Qt 6.12.0 source revisions for the shipped Core/Gui/Network/Widgets modules, Svg, Qt plugins, and any Qt code linked into those libraries;
- exact PySide6 and Shiboken source revisions and their third-party source/notice records;
- the Windows wheel artifacts and cryptographic hashes used by the build, provenance records, build configuration, compiler/toolchain inputs, patches and generated-code inputs;
- any modified source and build scripts/configuration required to produce the shipped libraries or user-modified versions, plus applicable third-party source and notices;
- the precise library/plugin versions constituting each Linked Version, and matching third-party component attributions/license texts;
- for §4(d)(0), the Minimal Corresponding Source and Corresponding Application Code and a procedure/terms that genuinely permit recipient recombination or relinking; or, for §4(d)(1), evidence of a suitable shared-library mechanism and its successful modified-library operation; and
- any Installation Information that counsel determines is required under §4(e), together with a description of any signing, installer, device or access controls relevant to installing a modified combined work.

Official Qt archives are available as source candidates, including [Qt 6.12.0 module source archives](https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/) and the [Qt for Python 6.12.0 source archive](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz). Their existence, matching version labels, and published archive digests do **not** establish they match the PySide6/Shiboken/Qt Windows binaries in this package. No such archive-to-binary verification is claimed here.

## 7. Requirements and evidence matrix

Status labels are limited to the evidence reviewed for this exact package: **Verified fact** means a direct package observation; **Upstream statement** means a public project/vendor statement not matched to the binary; **Open — not demonstrated** means the requirement/evidence has not been established; **Conditional** means applicability depends on conveyance or product facts and needs review.

| Topic | Conditional LGPLv3 issue / evidence needed | Status for trimmed package |
|---|---|---|
| Qt/PySide runtime present | Identify covered modules, bindings, plugins and linked versions. | **Verified fact:** Qt 6.12.0 Core, Gui, Network, Svg, Widgets, PySide6/Shiboken files and plugins are present. Exact source/build/license provenance is **open**. |
| Applicable license basis / election | Establish the exact license grants for every shipped Qt/PySide component and record the selected basis (LGPL, GPL or commercial where available). | **Upstream statement:** Qt and PyPI publish alternatives. **Open — not demonstrated:** no binary-specific election or commercial entitlement is established. PySide public descriptions differ on GPLv2. |
| Translation catalogs | Map each `.qm` to source and notices; distinguish catalogs from LGPL library binaries. | **Verified fact:** 99 catalogs present. **Upstream statement:** QUIP 18 gives usual translations as commercial OR BSD-3-Clause. Binary/source mapping and notice set **open**. |
| LGPL §4(a) notice | Prominent notice with each conveyed copy identifying LGPL library use and license coverage. | **Verified fact:** no notice text file in package. **Open — not demonstrated:** no package-matched end-user notice. |
| LGPL §4(b) texts | Accompany copy with GPL and LGPL texts. | **Verified fact:** neither text is in package; repository copies exist. **Open — not demonstrated** for this package. |
| LGPL §4(c) runtime display | If the application displays copyright notices, include Library notice and refer to license copies. | **Conditional:** runtime notice behavior was not audited for this issue; required notice/cross-reference is **open** if triggered. |
| LGPL §4(d)(0) source route | Convey Minimal Corresponding Source and Corresponding Application Code in suitable form/terms; source, build and relinking procedure must match the Linked Version. | **Open — not demonstrated:** no package-matched source/relink bundle or tested procedure. |
| LGPL §4(d)(1) shared-library route | Use recipient's/recipient-modified, interface-compatible library through a suitable shared-library mechanism. | **Verified fact:** modular onedir layout. **Open — not demonstrated:** exact-package replacement/load test absent; earlier different-package probe is insufficient. |
| Replacement scope | Validate the needed Qt DLL/plugin/binding set works together; preserve accessible paths and avoid blocking replacement. | **Open — not demonstrated:** no coherent modified-library set tested on this artifact. |
| Modification / reverse engineering | Distribution terms must not effectively restrict covered modification or reverse engineering to debug those modifications. | **Open — not demonstrated:** final EULA, installer, anti-tamper and user restrictions are unknown. |
| LGPL §4(e) installation info | Assess if otherwise required by GPLv3 §6; provide only the necessary installation/execution information for modified combined work. | **Conditional / open:** distribution device and security/signing restrictions are unknown; no determination made. |
| Third-party Qt/PySide components | Match source, license election and notices for embedded third-party code independently of Qt LGPL. | **Open:** multiple component versions, license alternatives, source mappings and notices remain unresolved in the final audit. |
| Source offer / access channel | Select a lawful conveyance method and ensure source availability and instructions match the actual linked release. | **Open:** no reviewed source/offer mechanism or retention/availability plan. |
| Release disposition | Legal review of actual final package, distribution channel, installer/EULA and complete obligations. | **Open — HOLD / NOT CLEARED FOR DISTRIBUTION.** |

This is an evidence matrix, not a finding that the project complies or fails any legal test. A verified absence of package notice files is a package fact; it is not, by itself, a final legal conclusion about a distribution that has not been authorized or made.

## 8. Options for a future authorized distribution

Subject to component-specific terms, evidence and qualified legal review, the project has several broad paths. None is approved by this assessment:

1. **Use an applicable LGPLv3 path** for the relevant Qt/PySide components and close the notice, source/relinking or suitable shared-library, modification-rights, any applicable installation-information, and third-party notice requirements described above.
2. **Use an applicable GPL path** only if the specific components are offered under that GPL option and the combined work and its conveyance satisfy the applicable GPL terms. This is not a shortcut around source obligations or the PySide license-expression discrepancy.
3. **Obtain and document applicable commercial rights** for Qt/Qt for Python if that route fits the product and distribution model. A commercial option does not automatically settle third-party component, Microsoft runtime, PyInstaller, CPython or other independent terms.
4. **Change the product/package scope** (for example, remove Qt/PySide or choose another GUI stack) if the required source, relinking, notices or rights cannot be established. Such a change requires a separate authorized engineering decision and a new package audit; it is not performed here.

The actual availability of each route for each binary remains subject to Qt's written confirmation, license texts, source/build provenance, any commercial agreement, third-party terms, and counsel's review.

## 9. Prioritized actions before any distribution decision

1. Obtain qualified counsel's review of LGPLv3 §4, both §4(d) routes, §4(e), the actual Windows conveyance and end-user restrictions, and the full release layout.
2. Obtain written Qt confirmation for the exact Qt/PySide6/Shiboken Windows distributions: applicable license alternatives/elections, GPLv2 metadata question, source/build identifiers, third-party attributions, and the VC++ DLL provenance issue recorded in the final audit.
3. Establish cryptographic provenance from the exact wheels/build inputs to the shipped Qt/PySide6/Shiboken files; collect matching source revisions, configuration, patches and component inventory/SBOM.
4. Map each of the 99 `.qm` catalogs and prepare the applicable translation/BSD notices separately from Qt LGPL library notices.
5. Decide which §4(d) approach is being relied upon. If shared-library replacement: conduct and document a recipient-controlled, exact-package modified-library test covering the coherent DLL/binding/plugin set. If source/relinking: assemble and test the corresponding source, application code, configuration, instructions and permissive terms. Do not count a test as legal clearance.
6. Prepare a reviewed user notice/license bundle in the authorized recipient delivery, including applicable GPL/LGPL copies, prominent Qt use notice, copyright/reference where required, resolved third-party attributions, and source/relinking information appropriate to the chosen route.
7. Review the installer, EULA, update/signing policy and Windows protections for effective restrictions; determine whether any Installation Information is required.
8. Re-inventory and hash the authorized final artifact, verify its notices and source route against that exact build, and rerun compatibility tests. Keep the disposition **HOLD** until the release owner and qualified counsel approve.

## 10. Dated official references

Public references consulted on **2026-11-09**. They explain upstream statements or license text; they do not prove provenance of the package binaries. Use versioned pages where available and preserve copies/hashes when building a future evidence set.

- Qt 6.12 licensing: [Qt Licensing](https://doc.qt.io/qt-6.12/licensing.html); [LGPL](https://doc.qt.io/qt-6.12/lgpl.html); [third-party code used in Qt](https://doc.qt.io/qt-6.12/licenses-used-in-qt.html); [Qt SBOM](https://doc.qt.io/qt-6.12/sbom.html).
- Qt for Python: [Commercial Use](https://doc.qt.io/qtforpython-6/commercial/index.html); [LGPL overview](https://doc.qt.io/qtforpython-6/overviews/qtdoc-lgpl.html); [third-party licenses used in Qt for Python](https://doc.qt.io/qtforpython-6/licenses.html).
- PySide6 6.12.0 public project metadata and description: [PyPI release page](https://pypi.org/project/PySide6/6.12.0/). This does not establish which wheel or build produced this package.
- Qt source/file-license classification: [QUIP 18 — License specification in Qt's modules](https://contribute.qt-project.org/quips/18/) (created 2022-09-26; active status shown on page), including its separate translation-file classification.
- Qt translation documentation: [Localizing Applications](https://doc.qt.io/qt-6.12/localization.html).
- Qt 6.12.0 source candidates: [Qt submodule archive directory](https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/); [PySide6 6.12.0 source archive](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz).
- Qt's own overview of [obligations of the GPL and LGPL](https://www.qt.io/development/open-source-lgpl-obligations).
- License text: [GNU LGPL v3](https://www.gnu.org/licenses/lgpl-3.0.html); LGPLv3 §4 incorporates terms from [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html). The text in the repository is available at `licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt`.
- Related package-specific repository evidence: `FINAL-LICENSING-AUDIT.md`, `TRIMMED-PACKAGE-NOTICE-MAP.md`, `qt/INVENTORY.md`, `RELEASE-PREPARATION-CHECKLIST.md`, and `notices/MANIFEST.md`.

## 11. Disposition and change control

**HOLD — NOT CLEARED FOR DISTRIBUTION.** The package's onedir layout and Qt DLL separation are useful engineering facts but do not establish LGPL compliance. Neither an LGPL license election, package-specific source match, completed notices, a qualifying replacement/relinking route, nor all required distribution terms have been demonstrated for this artifact. Qualified legal review and the evidence/actions above remain pending.

This assessment was prepared from read-only review of the package inventory and existing repository evidence. It does not modify, rebuild, replace, or authorize release of any binary. Existing source/spec/worktree changes, notice materials, tests and `release/` artifacts are to remain preserved. No commit or push is made.
