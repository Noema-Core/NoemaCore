// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/NoemaToken.sol";
import "../src/TrustLayer.sol";
import "../src/EscrowLayer.sol";
import "../src/RoutingLayer.sol";

contract DeployNoema is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        // Pobieramy prawdziwy adres portfela (EOA) z klucza prywatnego
        address deployer = vm.addr(deployerPrivateKey); 
        
        vm.startBroadcast(deployerPrivateKey);

        NoemaToken token = new NoemaToken(1_000_000_000);
        console.log("NoemaToken deployed at:", address(token));
        
        TrustLayer trust = new TrustLayer(address(token));
        console.log("TrustLayer deployed at:", address(trust));

        EscrowLayer escrow = new EscrowLayer(address(token), address(trust));
        console.log("EscrowLayer deployed at:", address(escrow));

        // Używamy 'deployer' zamiast 'msg.sender'
        RoutingLayer routing = new RoutingLayer(address(trust), address(token), deployer);
        console.log("RoutingLayer deployed at:", address(routing));

        vm.stopBroadcast();
    }
}
