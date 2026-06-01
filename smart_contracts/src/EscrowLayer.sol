// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./TrustLayer.sol";
import "./NoemaToken.sol";

contract EscrowLayer {
    IERC20 public paymentToken;
    TrustLayer public trustLayer;
    
    uint256 public jobCounter;
    
    enum JobStatus { PENDING, IN_PROGRESS, COMPLETED, DISPUTED, SLASHED }
    
    struct Job {
        address client;
        address worker;
        uint256 reward;
        uint256 deadline;
        JobStatus status;
        bytes32 dataHash;
    }
    
    mapping(uint256 => Job) public jobs;
    mapping(address => uint256[]) public clientJobs;
    mapping(address => uint256[]) public workerJobs;
    
    event JobCreated(uint256 jobId, address client, address worker, uint256 reward);
    event JobCompleted(uint256 jobId);
    event JobSlashed(uint256 jobId, address worker, uint256 slashedAmount);
    event JobRefunded(uint256 jobId, address client);
    
    constructor(address _token, address _trustLayer) {
        paymentToken = IERC20(_token);
        trustLayer = TrustLayer(_trustLayer);
    }
    
    function createJob(address worker, uint256 reward, uint256 durationInDays, bytes32 dataHash) external returns (uint256) {
        require(trustLayer.isVerified(msg.sender), "Client not verified in TrustLayer");
        require(trustLayer.isVerified(worker), "Worker not verified in TrustLayer");
        require(reward > 0, "Reward must be > 0");
        require(worker != msg.sender, "Cannot hire yourself");
        require(durationInDays > 0 && durationInDays <= 30, "Invalid duration");
        
        jobCounter++;
        uint256 deadline = block.timestamp + (durationInDays * 1 days);
        
        require(paymentToken.transferFrom(msg.sender, address(this), reward), "Token transfer failed");
        
        jobs[jobCounter] = Job({
            client: msg.sender,
            worker: worker,
            reward: reward,
            deadline: deadline,
            status: JobStatus.IN_PROGRESS,
            dataHash: dataHash
        });
        
        clientJobs[msg.sender].push(jobCounter);
        workerJobs[worker].push(jobCounter);
        
        emit JobCreated(jobCounter, msg.sender, worker, reward);
        return jobCounter;
    }
    
    function releaseFunds(uint256 jobId) external {
        Job storage job = jobs[jobId];
        require(msg.sender == job.client, "Only client can release funds");
        require(job.status == JobStatus.IN_PROGRESS, "Job not in progress");
        require(block.timestamp <= job.deadline, "Job deadline passed");
        
        job.status = JobStatus.COMPLETED;
        
        require(paymentToken.transfer(job.worker, job.reward), "Token transfer to worker failed");
        
        emit JobCompleted(jobId);
    }
    
    function slash(uint256 jobId) external {
        Job storage job = jobs[jobId];
        require(msg.sender == job.client, "Only client can slash");
        require(job.status == JobStatus.IN_PROGRESS, "Job not in progress");
        require(block.timestamp > job.deadline, "Deadline not passed yet");
        
        job.status = JobStatus.SLASHED;
        
        require(paymentToken.transfer(job.client, job.reward), "Refund failed");
        trustLayer.slash(job.worker, job.reward / 10, "Escrow: missed deadline");
        
        emit JobSlashed(jobId, job.worker, job.reward / 10);
    }
    
    function refund(uint256 jobId) external {
        Job storage job = jobs[jobId];
        require(msg.sender == job.client, "Only client can refund");
        require(job.status == JobStatus.IN_PROGRESS, "Job not in progress");
        require(block.timestamp > job.deadline, "Deadline not passed yet");
        
        job.status = JobStatus.PENDING;
        
        require(paymentToken.transfer(job.client, job.reward), "Refund failed");
        emit JobRefunded(jobId, job.client);
    }
}
