import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado com sucesso")
        return True
    except:
        print(f"❌ Erro ao instalar {package}")
        return False

print("Instalando dependências para embeddings...")

packages = [
    "sentence-transformers",
    "torch",
    "transformers",
    "llama-index-embeddings-huggingface"
]

for package in packages:
    install_package(package)

print("Instalação concluída!")