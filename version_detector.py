import winreg

def get_installed_programs():
    programs = []

    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]

    for path in paths:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:

                            # Проверяем, существуют ли нужные значения
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            except FileNotFoundError:
                                continue

                            try:
                                version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                            except FileNotFoundError:
                                version = "N/A"

                            programs.append((name, version))

                    except Exception:
                        continue
        except Exception:
            continue

    return programs


def find_version(program_name):
    programs = get_installed_programs()

    for name, version in programs:
        # Точное совпадение без учета регистра
        if name.strip().lower() == program_name.strip().lower():
            return version

    return "N/A"


def get_versions():
    return {
        "Securos": find_version("SecurOS"),
        "Auto": find_version("SecurOS Auto"),
        "NN-Auto": find_version("SecurOS NN-Server Auto for Intel"),
        "NN-Vehicle": find_version("SecurOS NN-Server Vehicle for Intel"),
    }


if __name__ == "__main__":
    versions = get_versions()
    for k, v in versions.items():
        print(f"{k}: {v}")