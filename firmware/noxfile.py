import nox


@nox.session(python="3")
def blacken(session):
    """Run black code formater."""
    session.install("black==19.3b0", "isort==4.3.21")
    files = ["noxfile.py", "code.py", "winterbloom_bhb"]
    session.run("isort", "--recursive", *files)
    session.run("black", *files)


@nox.session(python="3")
def lint(session):
    session.install("flake8==3.7.8", "black==19.3b0")
    files = ["noxfile.py", "code.py", "winterbloom_bhb"]
    session.run("black", "--check", *files)
    session.run("flake8", *files)
