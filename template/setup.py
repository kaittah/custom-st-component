from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-ai-assist",
    version="0.0.2",
    author="Kaitlyn Hennacy",
    author_email="kaitlynhennacy@gmail.com",
    description="A built in data analyst for your Streamlit app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        "streamlit>=1.34.0",
        "plotly>=5.22.0",
        "pydantic>=2.7.1",
        "pygithub>=2.3.0",
        "replicate>=0.26.0",
        "requests>=2.31.0",
        "scipy>=1.13.0",
        "snowflake-snowpark-python>=1.16.0",
        "snowflake-sqlalchemy>=1.5.1",
        "sqlalchemy>=1.4",
        "transformers>=4.41.0",
        "streamlit-mic-recorder"
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.39.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)
