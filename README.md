# S-Locus Finder Reporter Backend
An API REST for S-Locus Finder results databases.

## Development

### Requirements

S-Locus Finder Reporter Backend only requires an installation of Python 3.7.

### Conda environment (optional)

It is recommended, although not necessary, to use a Conda environment to develop S-Locus Finder Reporter.

[Here](https://docs.conda.io/en/latest/miniconda.html) you can find the installation instructions of Miniconda.

Once you have installed Conda, you can create and activate a new environment:

```bash
conda create -y -n s-locus-finder-reporter-backend python=3.7
conda activate s-locus-finder-reporter-backend
```

### Configuration

The only configuration needed to continue developing S-Locus Finder Reporter is to install the dependencies, which can
be done with the following command:

```bash
pip install -e .[dev]
```

### Building

S-Locus Finder Reporter can be build with the following command:

```bash
python3 -m build
```

This will generate two distributable files (`.tar.gz` and `.whl`) in the `dist` directory.

### Execution

The application can be launched in a GNU/Linux shell by executing from the project directory:

```bash
export PYTHONPATH=.
python s_locus_finder_reporter_backend/app.py
```
