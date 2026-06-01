// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title APIProviderRegistry (Light Version)
 * @dev Rejestr dostawców "niewykorzystanych limitów AI" - wersja bez zewnętrznych zależności
 */
contract APIProviderRegistry {
    
    address public owner;
    
    struct Provider {
        bytes32 metadataHash;
        string modelTag;
        uint256 dailyQuota;
        uint256 pricePerCall;
        bool isActive;
        uint256 registeredAt;
    }
    
    mapping(address => Provider) public providers;
    mapping(string => address[]) public modelProviders;
    
    event ProviderRegistered(address indexed provider, string model, uint256 quota);
    event ProviderUpdated(address indexed provider, bool isActive);
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    function registerProvider(
        bytes32 _metadataHash,
        string calldata _modelTag,
        uint256 _dailyQuota,
        uint256 _pricePerCall
    ) external {
        require(_dailyQuota > 0, "Quota must be positive");
        
        providers[msg.sender] = Provider({
            metadataHash: _metadataHash,
            modelTag: _modelTag,
            dailyQuota: _dailyQuota,
            pricePerCall: _pricePerCall,
            isActive: true,
            registeredAt: block.timestamp
        });
        
        modelProviders[_modelTag].push(msg.sender);
        emit ProviderRegistered(msg.sender, _modelTag, _dailyQuota);
    }
    
    function toggleActive(bool _active) external {
        require(providers[msg.sender].isActive, "Not registered");
        providers[msg.sender].isActive = _active;
        emit ProviderUpdated(msg.sender, _active);
    }
    
    function getActiveProviders(string calldata _modelTag) external view returns (address[] memory) {
        address[] memory allProviders = modelProviders[_modelTag];
        uint256 count = 0;
        for (uint256 i = 0; i < allProviders.length; i++) {
            if (providers[allProviders[i]].isActive) count++;
        }
        address[] memory active = new address[](count);
        uint256 idx = 0;
        for (uint256 i = 0; i < allProviders.length; i++) {
            address p = allProviders[i];
            if (providers[p].isActive) active[idx++] = p;
        }
        return active;
    }
    
    function slashProvider(address _provider, string calldata) external onlyOwner {
        require(providers[_provider].isActive, "Not active");
        providers[_provider].isActive = false;
    }
    
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Invalid address");
        owner = _newOwner;
    }
}
