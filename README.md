# Simple FastApi authentification

Simple authentification web-application using FastApi.

## Install

Python, Git and Poetry should be already installed.

1. Clone repository:

```console
git clone https://github.com/balancy/fastapi_simple_auth.git
```

2. Acivate a virtual environment inside cloned repository:

```console
poetry shell
```

3. Install requirements:

```console
poetry install
```

4. Rename .env.example to .env and define your proper environmental variables:
- `SALT` - salt to encode passwords
- `SECRET_KEY` - secret key to sign usernames
- `DATA_FILENAME` - path to json file containing users in format
```python
{
    "username1": {
        "name": "name",
        "password": "password",
        "balance": balance,
    },
}
```

## Run 

Run server:

```console
uvicorn server:app --reload
```