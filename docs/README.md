# Sphinx Documentation for DockerKernel

#### Install dependencies

- `pip install sphinx`
- `pip install commonmark`

#### Build Documentation

Navigate into the `docs/` directory and run `make html`.

#### Sphinx Autobuild

To have a live view of the documentation you can use `sphinx-autobuild`.
Install it via `pip install sphinx-autobuild` and run

```bash
sphinx-autobuild . _build/html
```

inside the `docs/` directory.
