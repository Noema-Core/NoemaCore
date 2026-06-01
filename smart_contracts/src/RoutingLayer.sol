// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {TrustLayer, IERC20} from "./TrustLayer.sol";

contract RoutingLayer {
    TrustLayer public trustLayer;
    IERC20 public paymentToken;
    address public treasury;

    uint256 public constant PROTOCOL_FEE_BPS = 200; 
    uint256 public constant BPS_DENOMINATOR = 10000;

    struct Service {
        address provider;
        string endpoint;
        uint256 pricePerCall;
        bool isActive;
    }

    mapping(address => mapping(address => uint256)) public deposits;
    mapping(bytes32 => mapping(address => Service)) public services;

    event Deposited(address indexed consumer, address indexed provider, uint256 amount);
    event Claimed(address indexed consumer, address indexed provider, uint256 amount, uint256 fee);
    event Withdrawn(address indexed consumer, address indexed provider, uint256 amount);
    event ServiceRegistered(bytes32 indexed serviceId, address indexed provider, string endpoint, uint256 pricePerCall);
    event ServiceDeactivated(bytes32 indexed serviceId, address indexed provider);

    constructor(address _trustLayer, address _token, address _treasury) {
        trustLayer = TrustLayer(_trustLayer);
        paymentToken = IERC20(_token);
        treasury = _treasury;
    }

    function deposit(address provider, uint256 amount) external {
        require(trustLayer.isVerified(provider), "Routing: Provider not verified");
        require(amount > 0, "Routing: Amount must be > 0");
        require(paymentToken.transferFrom(msg.sender, address(this), amount), "Routing: Transfer failed");
        deposits[msg.sender][provider] += amount;
        emit Deposited(msg.sender, provider, amount);
    }

    function claim(address consumer, uint256 amount) external {
        require(deposits[consumer][msg.sender] >= amount, "Routing: Insufficient deposit");
        deposits[consumer][msg.sender] -= amount;
        uint256 fee = (amount * PROTOCOL_FEE_BPS) / BPS_DENOMINATOR;
        uint256 payout = amount - fee;
        if (fee > 0) {
            require(paymentToken.transfer(treasury, fee), "Routing: Fee transfer failed");
        }
        if (payout > 0) {
            require(paymentToken.transfer(msg.sender, payout), "Routing: Payout transfer failed");
        }
        emit Claimed(consumer, msg.sender, amount, fee);
    }

    function withdraw(address provider, uint256 amount) external {
        require(deposits[msg.sender][provider] >= amount, "Routing: Insufficient balance");
        deposits[msg.sender][provider] -= amount;
        require(paymentToken.transfer(msg.sender, amount), "Routing: Withdraw failed");
        emit Withdrawn(msg.sender, provider, amount);
    }

    function registerService(bytes32 serviceId, string memory endpoint, uint256 pricePerCall) external {
        require(trustLayer.isVerified(msg.sender), "Routing: Provider not verified");
        require(pricePerCall > 0, "Routing: Price must be > 0");
        
        services[serviceId][msg.sender] = Service({
            provider: msg.sender,
            endpoint: endpoint,
            pricePerCall: pricePerCall,
            isActive: true
        });
        
        emit ServiceRegistered(serviceId, msg.sender, endpoint, pricePerCall);
    }

    function deactivateService(bytes32 serviceId) external {
        require(services[serviceId][msg.sender].provider == msg.sender, "Routing: Not your service");
        services[serviceId][msg.sender].isActive = false;
        emit ServiceDeactivated(serviceId, msg.sender);
    }
}