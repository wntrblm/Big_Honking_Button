# Copyright (c) 2021 Alethea Katherine Flowers.
# Published under the standard MIT License.
# Full text available at: https://opensource.org/licenses/MIT

import os
import os.path
import shutil
import subprocess
import sys

import jinja2
from __main__ import add_artifact

message_template = jinja2.Template(
    open(os.path.join(os.path.dirname(__file__), "template.jinja2"), "r").read()
)

def prepare_artifacts(info):
    os.chdir("factory")

    if os.path.exists("distribution"):
        shutil.rmtree("distribution")

    subprocess.run([sys.executable, "factory_setup.py", "publish"])

    print("Zipping up distribution...")
    os.chdir("distribution")
    subprocess.run(["zip", "-r", "-q", "distribution.zip", "."])

    os.chdir("../..")

    add_artifact(
        "factory/distribution/distribution.zip",
        f"big-honking-button-{info['tag']}.zip",
    )


def prepare_description(info, artifacts):
    return message_template.render(artifacts=artifacts, **info)
