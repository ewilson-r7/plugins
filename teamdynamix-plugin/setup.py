from setuptools import setup, find_packages

setup(
    name="icon_teamdynamix",
    version="1.0.0",
    description="TeamDynamix plugin for Rapid7 InsightConnect",
    author="your_org",
    packages=find_packages(),
    install_requires=["insightconnect_plugin_runtime", "requests"],
    entry_points={
        "console_scripts": [
            "icon_teamdynamix=icon_teamdynamix:main",
        ],
    },
)
