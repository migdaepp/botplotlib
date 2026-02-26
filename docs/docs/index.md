# botplotlib

<p align="center">
  <img src="images/the-future-is-cyborg-source.png" alt="the future is cyborg-source" width="500">
</p>

Matplotlib fed the scientific Python community for two decades and then AI showed up and tried to eat its lunch. botplotlib is us trying to build new community norms that work for everyone. We don't know what open-source looks like when collaborators are AI, so we decided to start with some very overengineered [GOVERNANCE.md](https://github.com/migdaepp/botplotlib/blob/main/GOVERNANCE.md) and [AGENTS.md](https://github.com/migdaepp/botplotlib/blob/main/AGENTS.md) files and a sandwich joke.

---

## Install

```bash
pip install git+https://github.com/migdaepp/botplotlib.git
```

For PNG export support (requires Cairo):

```bash
pip install "botplotlib[png] @ git+https://github.com/migdaepp/botplotlib.git"
```

## Tutorial

The interactive tutorial is a [marimo](https://marimo.io) notebook, because marimo is also ai-native and we think they are cool.

```bash
pip install marimo
marimo edit docs/tutorial.py
```

## What's next?

- [**Guide**](guide.md) — themes, plot types, data formats, JSON path, refactoring
- [**API Reference**](api/index.md) — full public API documentation
- [**Contributing**](contributing.md) — how to add to the project
