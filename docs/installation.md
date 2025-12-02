# Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlShabiliBadia/Kandidate.git
   cd Kandidate
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -e .[dev]
   pre-commit install
   ```
4. **Configure the app**
   ```bash
   cp config/default.yaml config/local.yaml
   # edit local.yaml to point repository.path somewhere writable
   ```
5. **Verify the toolchain**
   ```bash
   make lint
   make test
   ```
