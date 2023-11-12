from os import environ


class MissingEnvironmentKey(Exception):
    ...


def check_env_vars(variables: set[str]):
    absent_vars = variables.difference(environ.keys())

    if absent_vars:
        raise MissingEnvironmentKey(*absent_vars)
    