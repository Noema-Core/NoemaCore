// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/NoemaToken.sol";
import "../src/TrustLayer.sol";

contract DeployNoema is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);

        NoemaToken token = new NoemaToken(1_000_000_000);
        console.log("NoemaToken deployed at:", address(token));

        TrustLayer trust = new TrustLayer(address(token));
        console.log("TrustLayer deployed at:", address(trust));

        vm.stopBroadcast();
    }
}
