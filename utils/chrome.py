from pathlib import Path


def get_chrome_driver_path(full_browser_chrome_version: str):
    # Get major version number
    major_version = full_browser_chrome_version.split('.')[0]
    # Construct chromedriver path
    base_path = Path.cwd()
    driver_path = base_path / "chromedriver" / major_version / "chromedriver.exe"
    print(driver_path)
    if not driver_path.exists():
        raise FileNotFoundError(f"ChromeDriver not found for Chrome version {major_version}")

    return str(driver_path)
