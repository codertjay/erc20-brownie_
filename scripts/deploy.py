from brownie import OurToken
from helpful_scripts import get_account


def deploy():
    account = get_account()
    token = OurToken.deploy({'from': account}, 1000000000)
    print("Token was deployed",token.address)


def main():
    deploy()
