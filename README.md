# ForgeLang Core Engine
**A Domain-Specific Compiler for Real-Time RPG Memory Allocation**

ForgeLang is a custom programming language and compiler built to simulate how game engines handle player statistics and quest data. It features a custom Lexer, Parser, and Semantic Analyzer, along with a unique **Explainability Layer** that narrates the compilation process in real-time.

---

## 🛠️ Language Specification
ForgeLang uses a unique syntax designed for the "Forge" environment:

| Concept | ForgeLang Keyword | Definition |
| :--- | :--- | :--- |
| **Integer** | `hp` | Stores whole numeric stats (4 Bytes). |
| **Float** | `xp` | Stores precise decimal values (4 Bytes). |
| **String** | `lore` | Stores dialogue or descriptions (64 Bytes). |
| **Boolean** | `status` | Stores binary flags/buffs (2 Bytes). |
| **Assignment** | `equip` | Binds a value to an identifier. |
| **Delimiter** | `done` | Marks the end of a statement. |
| **Output** | `spawn` | Renders a variable to the terminal. |

---

## ✨ Key Features
* **Explainability Layer:** The compiler "talks" to the user, providing a narrative log of Lexical, Syntactic, and Semantic phases.
* **Dynamic Symbol Table:** A live-updating memory map showing Scope Levels, Memory Offsets, and Byte Widths.
* **Voice-to-Code:** Integrated Web Speech API allowing developers to "scribe" code using voice commands.
* **ALU Support:** Handles dynamic arithmetic during assignment (e.g., `50 times 2`).
* **Scoping Logic:** Supports `begin` and `close` blocks for local memory management.
