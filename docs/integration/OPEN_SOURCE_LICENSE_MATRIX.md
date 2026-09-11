# Open-Source License & Distribution Matrix

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `feature/open-source-mainframe-reference-stack`  
**Date:** September 2, 2026  

---

## 1. Selected Components & License Compatibility

| Component | Version | License | Source URL | Usage Type | Distribution Implication | Compatible with Project? |
|---|---|---|---|---|---|---|
| **ICU4J** | `74.2` | Unicode-DFS-2016 / ICU License | [github.com/unicode-org/icu](https://github.com/unicode-org/icu) | Library (Compile & Test) | Permissive (BSD/MIT-style). May be distributed freely in binary or source form. | **YES** |
| **z390** | `1.5.x` | ASTC Open Source / GPLv2 Compatible | [github.com/z390development/z390](https://github.com/z390development/z390) | Tooling / Reference Oracle Only | Isolated test-time tool only. Not bundled into generated production Java. | **YES** |
| **Hercules / Hyperion** | `4.x` | QPL (Q Public License) | [github.com/sdl-hercules-390/hyperion](https://github.com/sdl-hercules-390/hyperion) | Optional Tooling / Reference Oracle Only | Isolated external container execution only. No binary linking with core project. | **YES** |
| **GnuCOBOL** | `3.x` | GPLv3 / LGPLv3 | [savannah.gnu.org/projects/gnucobol](https://savannah.gnu.org/projects/gnucobol) | Baseline Container Oracle | Isolated Docker execution. No runtime linking into generated Java. | **YES** |
| **PostgreSQL JDBC** | `42.7.x` | BSD-2-Clause | [jdbc.postgresql.org](https://jdbc.postgresql.org) | Modernized Spring Boot Runtime Dependency | Permissive BSD license. Standard cloud enterprise distribution. | **YES** |
| **H2 Database** | `2.2.x` | MPL 2.0 / EPL 1.0 | [h2database.com](http://www.h2database.com) | Test Dependency Only | Permissive copyleft for file changes; test scope only. | **YES** |

---

## 2. Strict Architectural Safeguards

1. **Zero Contamination of Production Java:**
   - No GPL, QPL, or emulator code is imported, linked, or embedded into the generated Spring Boot / Java application.
   - The generated application depends exclusively on standard Java standard library and Spring Framework ecosystem dependencies.

2. **Isolated Tooling Layer:**
   - Reference runtimes (`z390`, `Hercules`, `GnuCOBOL`) run strictly as out-of-process CLI/Docker binaries in temporary, isolated directories.
