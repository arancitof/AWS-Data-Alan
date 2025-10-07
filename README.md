<span style="color:blue;">🚀 Guía de Instalación para Entorno de Desarrollo en Ubuntu WSL</span>

Este README proporciona una guía detallada para la configuración de un entorno de desarrollo robusto utilizando Ubuntu en Windows Subsystem for Linux (WSL). Incluye los pasos para instalar Python, Docker, Docker Compose, Virtual Env y Jupyter Notebook, junto con las verificaciones y fuentes de referencia.

<span style="color:blue;">🐍 Python 12</span>

Comandos Ubuntu WSL usados	Comprobación	Fuentes citadas
python3 --version	Se verifica la versión de Python instalada.	
	Resultado: Python 3.12.3 ya viene instalado por defecto en Ubuntu 24.	

  <span style="color:blue;">🐳 Docker y Docker Compose</span>

Comandos Ubuntu WSL usados	Comprobación	Fuentes citadas
docker --version	Se verifica si Docker ya está instalado.	Youtube - Instalación de Docker en WSL
sudo apt install apt-transport-https ca-certificates curl software-properties-common	Se instalan las dependencias necesarias.	GitHub - Scripts para Docker en WSL
`curl -fsSL https://download.docker.com/linux/ubuntu/gpg	sudo apt-key add -<br>sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"`	Se agrega el repositorio oficial de Docker.
sudo apt update sudo apt install docker-ce docker-ce-cli containerd.io	Se actualizan los paquetes y se instala Docker Engine, Docker CLI y Containerd.	Documentación oficial de Docker para Ubuntu
wsl --shutdown	Se reinicia WSL para asegurar la correcta instalación.	
docker --version docker run hello-world	Se comprueba la instalación de Docker y su funcionamiento básico.	
sudo apt update sudo apt install docker-compose-plugin	Se actualizan los paquetes y se instala Docker Compose como un plugin de Docker.	Documentación oficial de Docker Compose

<span style="color:blue;">📦 Virtual Env</span>

Comandos Ubuntu WSL usados	Comprobación	Fuentes citadas
sudo apt install python3-venv o pip install virtualenv	Se instala Virtual Env, ya sea a través de apt para la herramienta venv de Python 3 o de forma global con pip.	Virtualenv - Instalación
	Se puede verificar su instalación intentando crear un entorno virtual: python3 -m venv myenv	Microsoft Learn - Configuración del entorno de desarrollo de WSL

<span style="color:blue;">📝 Jupyter Notebook</span>

Comandos Ubuntu WSL usados	Comprobación	Fuentes citadas
sudo apt-get install python3-pip	Se instala pip (gestor de paquetes de Python) si aún no está disponible.	Saturn Cloud - Cómo instalar Jupyter Notebook en Ubuntu
pip install notebook	Se instala Jupyter Notebook utilizando pip.	Jupyter - Instalación
	Para comprobar la instalación, simplemente ejecuta jupyter notebook en la terminal.
