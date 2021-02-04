import functools
import os
from pathlib import Path
import subprocess
from cryptography.hazmat.backends import \
    default_backend as crypto_default_backend
from cryptography.hazmat.primitives import \
    serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import git
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
   return pub_key

@print_func
def configure_deploy_key(pub_key):
   print("You need to add the contents of your public key to GitHub.")
   print("It is recommended that you add this as a deploy key to the repository.")
   print("For instructions on how to do this, please visit:")
   print("\thttps://docs.flsvc.net/docs/add-deploy-key")
   print("Once you have done this, come back to this terminal, and type y")
   print("##################################")
   print("###START FILE#####################")
   print(pub_key.decode("utf-8"))
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

@print_fund
def setup_pipenv(repo_dir):
   status = subprocess.call(['pipenv', 'install', '--dev'],
                            cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   if return_code != 0:
      print("pipenv install failed:")
      for line in status.stdout.readlines():
         print(line.strip())

def main():
   print("Starting user configuration script.")
   user_home = str(Path.home())
   print(f"Using home directory: {user_home}")
   pub_key = configure_ssh(user_home)
   configure_deploy_key(pub_key)
   repo_url = "git@github.com:dgaiero/ee542.git"
   repo_dir = os.path.join(user_home, "workspace", "ee542")
   clone_repo(repo_url, repo_dir, "dev")
   setup_pipenv(repo_dir)

if __name__ == "__main__":
   main()