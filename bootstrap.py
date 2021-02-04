import functools
import os
import subprocess
from pathlib import Path

import json
import git
import shutil
from cryptography.hazmat.backends import \
    default_backend as crypto_default_backend
from cryptography.hazmat.primitives import \
    serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm


def print_func(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        print(f"running {f.__name__}")
        return f(*args, **kwargs)
    return wrapped


@print_func
def generate_keys():
   """Generates public/private RSA keys."""
   key = rsa.generate_private_key(
      backend=crypto_default_backend(),
      public_exponent=65537,
      key_size=4096
   )
   private_key = key.private_bytes(
      crypto_serialization.Encoding.PEM,
      crypto_serialization.PrivateFormat.PKCS8,
      crypto_serialization.NoEncryption())
   public_key = key.public_key().public_bytes(
      crypto_serialization.Encoding.OpenSSH,
      crypto_serialization.PublicFormat.OpenSSH
   )
   return private_key, public_key


@print_func
def write_ssh_file(ssh_path, filename, data):
   file_path = os.path.join(ssh_path, filename)
   file_exist = os.path.isfile(file_path)
   create_file = True
   if file_exist:
      create_file = confirm(f"{file_path} already exists. Overwrite?")
   if create_file:
      print(f"Writing {file_path}")
      f = open(file_path, 'wb')
      f.write(data)
      f.close()
   return file_exist


@print_func
def configure_ssh(user_home):
   ssh_path = os.path.join(user_home, ".ssh")
   Path(ssh_path).mkdir(parents=True, exist_ok=True)
   priv_key, pub_key = generate_keys()
   write_ssh_file(ssh_path, "id_rsa", priv_key)
   file_exist = write_ssh_file(ssh_path, "id_rsa.pub", pub_key)
   if file_exist:
      fd = open(os.path.join(ssh_path, "id_rsa.pub"), "rb")
      pub_key = fd.read()
      fd.close()
      os.chmod(ssh_path, 400)
   return pub_key

@print_func
def configure_ssh_key(pub_key):
   print("You need to add the contents of your public key to GitHub.")
   print("For instructions on how to do this, please visit:")
   print("\thttps://bit.ly/gh-ssh")
   print("Once you have done this, come back to this terminal, and type y")
   print("##################################")
   print("###START FILE#####################")
   print(pub_key.decode("utf-8").strip('\n'))
   print("###END FILE#######################")
   print("##################################")
   copy = False
   while not(copy):
      copy = confirm(f"Have you copied the contents of the file to GitHub?")

@print_func
def clone_repo(repo_url, repo_dir, branch):
   Path(repo_dir).mkdir(parents=True, exist_ok=True)
   repo = git.Repo.clone_from(repo_url, repo_dir)
   print(f"checking out {branch} branch")
   repo.git.checkout(branch)
   log_dir = os.path.join(repo_dir, "logs")
   Path(log_dir).mkdir(parents=True, exist_ok=True)

@print_func
def setup_pipenv(repo_dir):
   status = subprocess.run(['pipenv', 'install', '--dev'], \
                            cwd=repo_dir, capture_output=True, text=True)
   if status.returncode != 0:
      print("pipenv install failed:")
      print(status.stdout)

@print_func
def create_env(repo_dir):
   file_path = os.path.join(repo_dir, ".env")
   f = open(file_path, 'w')
   f.write("PYTHONPATH=${PYTHONPATH}:${PWD}\n")
   f.close()

@print_func
def get_venv_location(repo_dir):
   venv_python = subprocess.run(['pipenv', '--venv'],
                                cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   venv_location = venv_python.stdout.decode("utf-8").strip('\n')
   venv_location = os.path.join(venv_location, "bin", "python")
   return venv_location

@print_func
def configure_vscode(repo_dir):
   cwd = os.path.dirname(os.path.realpath(__file__))
   shutil.copytree(os.path.join(cwd, "_config/.vscode"),
      os.path.join(repo_dir, ".vscode"))

   venv_location = get_venv_location(repo_dir)
   vscode_settings_location = os.path.join(repo_dir, ".vscode", "settings.json")
   with open(vscode_settings_location) as f:
      vscode_settings_file = json.load(f)
   vscode_settings_file['python.pythonPath'] = venv_location
   with open(vscode_settings_location, 'w') as json_file:
      json.dump(vscode_settings_file, json_file)

@print_func
def copy_bash_aliases(user_home):
   cwd = os.path.dirname(os.path.realpath(__file__))
   src_file = os.path.join(cwd, "_config", "$user", ".bash_aliases")
   dst_file = os.path.join(user_home, ".bash_aliases")
   shutil.copy2(src_file, dst_file)


def main():
   print("Starting user configuration script.")
   user_home = str(Path.home())
   repo_url = "git@github.com:dgaiero/ee542.git"
   repo_dir = os.path.join(user_home, "workspace", "ee542")
   print(f"Using home directory: {user_home}")
   copy_bash_aliases(user_home)
   pub_key = configure_ssh(user_home)
   configure_ssh_key(pub_key)
   clone_repo(repo_url, repo_dir, "dev")
   setup_pipenv(repo_dir)
   create_env(repo_dir)
   configure_vscode(repo_dir)

if __name__ == "__main__":
   main()
