from brownie import (
    network, accounts, config, VRFCoordinatorMock,
    MockV3Aggregator, Contract, LinkToken)
from web3 import Web3

DECIMALS = 8
STARTING_PRICE = 200000000000
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'ganache-local']
FORKED_LOCAL_ENVIRONMENTS = ['mainnet-fork-dev',
                             'development', 'mainnet-fork']


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active(
    ) in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config['wallets']['from_key'])


contract_to_mock = {
    'eth_usd_price_feed': MockV3Aggregator,
    'vrf_coordinator': VRFCoordinatorMock,
    'link_token': LinkToken
}


def get_contract(contract_name):
    """
    This function will grab the contract addresses from brownie config
    if define otherwise it would deploy a mock version and
    return that mock contract

    Args:
        contract_name (String)
    Returns:
        brownie.network.contract.ProjectContract: The most recently
        deployed version of the contract
        MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]
    else:
        # on real network
        contract_address = config['networks'][network.show_active()][
            contract_name
        ]
        # Address
        # ABI
        contract = Contract.from_abi(
            contract_type._name,
            contract_address,
            contract_type.abi)
        # MockV3Aggregator.abi
    return contract


def deploy_mocks():
    account = get_account()
    print('Deploying Mocks ...')
    mock = MockV3Aggregator.deploy(
        DECIMALS, STARTING_PRICE,
        {'from': account}
    )
    print('Mocks Deployed.')
    print('Deploying Link ...')
    link_token = LinkToken.deploy({'from': account})
    print('Link Deployed.')
    print('Deploying VRFCoordinatorMock ...')
    VRFCoordinatorMock.deploy(
        link_token.address, {'from': account}
    )
    print('VRFCoordinatorMock Deployed.')


def fund_with_link(contract_address, account=None,
                   link_token=None, amount=300000000000000000):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract('link_token')
    # link_token_contract = interfaces.LinkTokenInterface(
    #     link_token.address)
    # tx = link_token_contract.transfer(
    #     contract_address, amount,
    #     {'from': account})
    tx = link_token.transfer(
        contract_address, amount,
        {'from': account})
    tx.wait(1)
    print('Fund Contract!')
    return tx
