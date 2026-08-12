import logging
import winreg
from pathlib import Path

logger = logging.getLogger(__name__)

WINREG_GAME_KEYS = [
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\KRInstall Wuthering Waves",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\KRInstall Wuthering Waves Overseas",
]


def get_install_path() -> str | None:
    for key_str in WINREG_GAME_KEYS:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_str) as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                if not install_path:
                    logger.info(f"A chave do Registro existe, mas InstallPath está vazio: {key_str}")
                    continue
                logger.debug("install_path: %s", install_path)
                program_path = Path(install_path).joinpath("Wuthering Waves Game/Wuthering Waves.exe")
                logger.debug(f"Caminho do jogo lido do Registro: {program_path}")
                return str(program_path)
        except FileNotFoundError:
            logger.debug(f"O caminho do Registro não existe: {key_str}")
        except PermissionError:
            logger.warning(f"Sem permissão para acessar a chave do Registro: {key_str}")
        except Exception:
            logger.exception(f"Erro ao ler a chave do Registro {key_str}")
    return None
