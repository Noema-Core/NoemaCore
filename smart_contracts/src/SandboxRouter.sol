// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Minimalny interfejs ERC20 (zamiast zewnętrznej biblioteki)
interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

// Interfejsy wewnętrzne
interface IEscrowLayer {
    function createJob(address worker, uint256 reward, uint256 duration, bytes32 metadata) external returns (uint256);
    function releaseFunds(uint256 jobId) external;
}

interface ITrustLayer {
    function isVerified(address agent) external view returns (bool);
    function slash(address agent, uint256 amount, string memory reason) external;
}

/**
 * @title SandboxRouter
 * @dev Koordynuje wykonanie zadań w izolowanym sandboxie + rozliczenia on-chain
 */
contract SandboxRouter {
    struct ExecutionRequest {
        address client;
        address provider;
        uint256 reward;
        bytes32 taskHash;
        uint256 deadline;
        bool completed;
        bytes32 attestationHash;
        uint256 escrowJobId;
    }

    event ExecutionRequested(bytes32 indexed executionId, address indexed client, address indexed provider, uint256 reward, uint256 deadline);
    event ExecutionCompleted(bytes32 indexed executionId, bytes32 attestationHash, uint256 timestamp);
    event ExecutionSlashed(bytes32 indexed executionId, address provider, string reason);

    address public immutable token;
    address public immutable trustLayer;
    address public immutable escrowLayer;
    address public owner;

    mapping(bytes32 => ExecutionRequest) public executions;
    uint256 public executionCounter;
    uint256 public constant MAX_TIMEOUT = 24 hours;

    modifier onlyOwner() {
        require(msg.sender == owner, "SandboxRouter: Not owner");
        _;
    }

    constructor(address _token, address _trustLayer, address _escrowLayer) {
        token = _token;
        trustLayer = _trustLayer;
        escrowLayer = _escrowLayer;
        owner = msg.sender;
    }

    function requestExecution(address _provider, bytes32 _taskHash, uint256 _reward, uint256 _timeout) external returns (bytes32 executionId) {
        require(ITrustLayer(trustLayer).isVerified(_provider), "Provider not verified");
        require(_reward > 0 && _timeout <= MAX_TIMEOUT, "Invalid params");

        // 1. Transfer tokenów do Escrow
        require(IERC20(token).transferFrom(msg.sender, escrowLayer, _reward), "Transfer failed");

        // 2. Utwórz job w Escrow
        uint256 jobId = IEscrowLayer(escrowLayer).createJob(_provider, _reward, _timeout, _taskHash);

        // 3. Generuj executionId i zapisz żądanie
        executionId = keccak256(abi.encodePacked(block.timestamp, msg.sender, _provider, executionCounter++));
        executions[executionId] = ExecutionRequest({
            client: msg.sender,
            provider: _provider,
            reward: _reward,
            taskHash: _taskHash,
            deadline: block.timestamp + _timeout,
            completed: false,
            attestationHash: bytes32(0),
                                                   escrowJobId: jobId
        });

        emit ExecutionRequested(executionId, msg.sender, _provider, _reward, executions[executionId].deadline);
    }

    function submitAttestation(bytes32 _executionId, bytes32 _attestationHash) external {
        ExecutionRequest storage exec = executions[_executionId];
        require(exec.client != address(0), "Execution not found");
        require(!exec.completed, "Already completed");
        require(msg.sender == exec.provider, "Only provider");
        require(block.timestamp <= exec.deadline, "Deadline passed");
        require(_attestationHash != bytes32(0), "Invalid attestation");

        exec.completed = true;
        exec.attestationHash = _attestationHash;

        // 4. Zwolnij środki z Escrow dla providera
        IEscrowLayer(escrowLayer).releaseFunds(exec.escrowJobId);
        emit ExecutionCompleted(_executionId, _attestationHash, block.timestamp);
    }

    function slashTimeout(bytes32 _executionId) external {
        ExecutionRequest storage exec = executions[_executionId];
        require(exec.client != address(0), "Execution not found");
        require(!exec.completed, "Already completed");
        require(block.timestamp > exec.deadline, "Deadline not passed");

        exec.completed = true;
        ITrustLayer(trustLayer).slash(exec.provider, exec.reward / 10, "Sandbox timeout");
        emit ExecutionSlashed(_executionId, exec.provider, "Deadline exceeded");
    }

    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Invalid address");
        owner = _newOwner;
    }
}
