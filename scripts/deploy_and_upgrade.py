from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    Contract,
    BoxV2,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=True)

    # Hook it up on a proxy

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account},
        publish_source=True,
    )

    print(f"Proxy deployed to {proxy}, you can now upgrade to v2")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    tx = proxy_box.store(3, {"from": account})
    tx.wait(1)
    print(proxy_box.retrieve())

    # upgrade
    boxV2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_transaction = upgrade(
        account, proxy, boxV2.address, proxy_admin_contract=proxy_admin
    )
    print("Proxy has been upgraded")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
