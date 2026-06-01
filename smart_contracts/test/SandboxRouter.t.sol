// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test, console} from "forge-std/Test.sol";
import {SandboxRouter} from "../src/SandboxRouter.sol";

// --- Mocki ---

contract MockToken {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    function mint(address to, uint256 amount) external { balanceOf[to] += amount; }
    function approve(address spender, uint256 amount) external returns (bool) { allowance[msg.sender][spender] = amount; return true; }
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(allowance[from][msg.sender] >= amount, "Allowance");
        require(balanceOf[from] >= amount, "Balance");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

contract MockTrustLayer {
    function isVerified(address) external pure returns (bool) { return true; }
    function slash(address, uint256, string memory) external {}
}

contract MockEscrowLayer {
    uint256 public jobIdCounter;
    function createJob(address, uint256, uint256, bytes32) external returns (uint256) {
        return ++jobIdCounter;
    }
    function releaseFunds(uint256) external {}
}

// --- Testy ---

contract SandboxRouterTest is Test {
    SandboxRouter public router;
    MockToken public token;
    MockTrustLayer public trust;
    MockEscrowLayer public escrow;
    
    address owner = address(0x1);
    address client = address(0x2);
    address provider = address(0x3);
    uint256 reward = 100 * 10**18;
    bytes32 taskHash = keccak256("print('hello')");

    function setUp() public {
        token = new MockToken();
        trust = new MockTrustLayer();
        escrow = new MockEscrowLayer();
        
        vm.prank(owner);
        router = new SandboxRouter(address(token), address(trust), address(escrow));
        
        token.mint(client, reward * 10);
        vm.prank(client);
        token.approve(address(router), type(uint256).max);
    }

    function test_RequestExecution() public {
        vm.prank(client);
        bytes32 execId = router.requestExecution(provider, taskHash, reward, 3600);
        
        // executionId to hash, więc sprawdzamy tylko że nie jest zerowy
        assertTrue(execId != bytes32(0), "executionId should not be zero");
        
        // Weryfikacja stanu przez mapping
        (address c, address p, uint256 r, bytes32 tHash, uint256 deadline, bool done, ,) = router.executions(execId);
        assertEq(c, client);
        assertEq(p, provider);
        assertEq(r, reward);
        assertEq(tHash, taskHash);
        assertEq(done, false);
        assertGt(deadline, block.timestamp);
    }

    function test_SubmitAttestation() public {
        vm.prank(client);
        bytes32 execId = router.requestExecution(provider, taskHash, reward, 3600);
        
        bytes32 attestation = keccak256("task|output||1.5");
        vm.prank(provider);
        router.submitAttestation(execId, attestation);
        
        (,,,,, bool completed, bytes32 storedHash,) = router.executions(execId);
        assertEq(completed, true);
        assertEq(storedHash, attestation);
    }

    function test_SlashTimeout() public {
        vm.prank(client);
        bytes32 execId = router.requestExecution(provider, taskHash, reward, 1);
        
        vm.warp(block.timestamp + 2);
        
        router.slashTimeout(execId);
        
        (,,,,, bool completed,,) = router.executions(execId);
        assertEq(completed, true);
    }

    function test_Revert_UnverifiedProvider() public {
        vm.prank(client);
        vm.expectRevert();
        router.requestExecution(provider, taskHash, 0, 3600);
    }
}
