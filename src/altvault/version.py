from debian.debian_support import Version


def safe_version(version_string: str) -> Version:
    try:
        return Version(version_string)
    except ValueError:
        return Version(version_string.replace("_", ""))
