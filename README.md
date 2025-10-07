# <span style="color: #0066cc;">🚀 Guía de Instalación - Entorno de Desarrollo en Ubuntu WSL</span>

## <span style="color: #0066cc;">📋 Descripción</span>

Esta guía proporciona los pasos detallados para configurar un entorno de desarrollo completo en **Ubuntu 24 WSL** con las siguientes tecnologías:

- Python 3.12.3
- Docker & Docker Compose
- Virtual Environment (venv)
- Jupyter Notebook

---

## <span style="color: #0066cc;">📦 Tabla de Instalación</span>

| Tecnología | Comandos Ubuntu WSL | Comprobación | Fuentes |
|------------|---------------------|--------------|---------|
| **Python 3.12** | `python3 --version` | `python3 --version` | Pre-instalado en Ubuntu 24 |
| **Docker** | Ver sección Docker | `docker --version`<br>`docker run hello-world` | [YouTube Tutorial](https://www.youtube.com/watch?v=cIkwQWGBbIs&t=101s)<br>[GitHub Scripts](https://github.com/SoyITPro/scripts/tree/main/Docker/install_docker_wsl)<br>[Docker Docs Ubuntu](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) |
| **Docker Compose** | `sudo apt update`<br>`sudo apt install docker-compose-plugin` | `docker-compose --version` | [Docker Compose Install](https://docs.docker.com/compose/install/) |
| **Virtual Environment** | `sudo apt install python3-venv`<br>o `pip install virtualenv` | `python3 -m venv --help` | [Virtualenv Docs](https://virtualenv.pypa.io/en/latest/installation.html)<br>[Microsoft WSL Docs](https://learn.microsoft.com/es-es/windows/wsl/setup/environment) |
| **Jupyter Notebook** | `sudo apt-get install python3-pip`<br>`pip install notebook` | `jupyter notebook --version` | [Saturn Cloud Tutorial](https://saturncloud.io/blog/how-to-install-jupyter-notebook-in-ubuntu/)<br>[Jupyter Official](https://jupyter.org/install) |

---

## <span style="color: #0066cc;">🐍 1. Python 3.12</span>

### Verificación de Instalación

Python viene pre-instalado en Ubuntu 24. Para verificar la versión instalada:

```bash
python3 --version
```

**Salida esperada:**
```
Python 3.12.3
```

> ℹ️ **Nota:** Python 3.12.3 ya está incluido por defecto en Ubuntu 24.

---

## <span style="color: #0066cc;">🐳 2. Docker & Docker Compose</span>

### Paso 1: Verificar si Docker está instalado

```bash
docker --version
```

### Paso 2: Instalar Dependencias Necesarias

```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

### Paso 3: Agregar el Repositorio Oficial de Docker

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

### Paso 4: Actualizar Paquetes e Instalar Docker

```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

### Paso 5: Reiniciar WSL

Para asegurar que la instalación se complete correctamente:

```bash
wsl --shutdown
```

> ⚠️ **Importante:** Ejecutar este comando desde PowerShell o CMD en Windows, no desde WSL.

### Paso 6: Verificar Instalación de Docker

```bash
docker --version
docker run hello-world
```

### Paso 7: Instalar Docker Compose Plugin

Docker Compose es un plugin de Docker. Para instalarlo:

```bash
sudo apt update
sudo apt install docker-compose-plugin
```

### Verificación de Docker Compose

```bash
docker-compose --version
```

### 📚 Fuentes Docker
- [Tutorial en YouTube](https://www.youtube.com/watch?v=cIkwQWGBbIs&t=101s)
- [Scripts de Instalación - GitHub](https://github.com/SoyITPro/scripts/tree/main/Docker/install_docker_wsl)
- [Documentación Oficial Docker Ubuntu](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)
- [Documentación Docker Compose](https://docs.docker.com/compose/install/)

---

## <span style="color: #0066cc;">🌐 3. Virtual Environment (venv)</span>

Virtual Environment es una herramienta que requiere un intérprete de Python y puede instalarse de dos formas:

### Opción 1: Instalación Local (Recomendada)

```bash
sudo apt install python3-venv
```

### Opción 2: Instalación Global con pip

```bash
pip install virtualenv
```

### Verificación

```bash
python3 -m venv --help
```

### Crear un Entorno Virtual

```bash
python3 -m venv nombre_entorno
source nombre_entorno/bin/activate
```

### 📚 Fuentes Virtual Environment
- [Documentación Oficial Virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
- [Microsoft WSL Environment Setup](https://learn.microsoft.com/es-es/windows/wsl/setup/environment)

---

## <span style="color: #0066cc;">📓 4. Jupyter Notebook</span>

Jupyter Notebook se instala utilizando **pip** (gestor de paquetes para Python).

### Paso 1: Instalar pip

```bash
sudo apt-get install python3-pip
```

### Paso 2: Instalar Jupyter Notebook

```bash
pip install notebook
```

### Verificación

```bash
jupyter notebook --version
```

### Iniciar Jupyter Notebook

```bash
jupyter notebook
```

### 📚 Fuentes Jupyter Notebook
- [Tutorial Saturn Cloud](https://saturncloud.io/blog/how-to-install-jupyter-notebook-in-ubuntu/)
- [Documentación Oficial Jupyter](https://jupyter.org/install)

---

## <span style="color: #0066cc;">✅ Verificación Completa del Entorno</span>

Ejecuta los siguientes comandos para verificar que todo esté correctamente instalado:

```bash
# Python
python3 --version

# Docker
docker --version
docker run hello-world

# Docker Compose
docker-compose --version

# Virtual Environment
python3 -m venv --help

# Jupyter Notebook
jupyter notebook --version
```

---

## <span style="color: #0066cc;">🛠️ Comandos Útiles</span>

### Docker
```bash
# Ver contenedores en ejecución
docker ps

# Ver todas las imágenes
docker images

# Detener todos los contenedores
docker stop $(docker ps -aq)
```

### Virtual Environment
```bash
# Activar entorno virtual
source nombre_entorno/bin/activate

# Desactivar entorno virtual
deactivate
```

### Jupyter Notebook
```bash
# Iniciar Jupyter en un puerto específico
jupyter notebook --port 8888

# Listar kernels disponibles
jupyter kernelspec list
```

---

## <span style="color: #0066cc;">📝 Notas Adicionales</span>

- **WSL (Windows Subsystem for Linux):** Asegúrate de tener WSL 2 instalado para mejor rendimiento con Docker.
- **Permisos Docker:** Si encuentras problemas de permisos, agrega tu usuario al grupo docker:
  ```bash
  sudo usermod -aG docker $USER
  ```
  Luego cierra sesión y vuelve a iniciarla.

---

## <span style="color: #0066cc;">📄 Licencia</span>

Este documento es de uso libre para fines educativos y de desarrollo.

---

## <span style="color: #0066cc;">👤 Autor</span>

Documentación creada para configuración de entorno de desarrollo en Ubuntu WSL.

---

**Última actualización:** Octubre 2025
