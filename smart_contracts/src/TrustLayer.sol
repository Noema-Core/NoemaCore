// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title TrustLayer
 * @dev Filar 1 Architektury T.R.E. - Zarządzanie tożsamością i stakingiem dla Agentów AI.
 */

// Minimalny interfejs ERC20 potrzebny do obsługi tokena
interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
}

contract TrustLayer {
    IERC20 public stakingToken;

    // Minimalna ilość tokenów do stakingu (100 tokenów, zakładając 18 miejsc po przecinku)
    uint256 public constant MIN_STAKE = 100 * 10**18;

    // Mapowanie: Adres portfela Agenta -> Ilość zastawionych tokenów
    mapping(address => uint256) public stakedBalance;

    // Mapowanie: Adres portfela Agenta -> Status Weryfikacji (True/False)
    mapping(address => bool) public isVerified;

    // Zdarzenia (Events) do śledzenia w SDK Python
    event Staked(address indexed agent, uint256 amount);
    event Unstaked(address indexed agent, uint256 amount);
    event Slashed(address indexed agent, uint256 amount, string reason);

    constructor(address _tokenAddress) {
        stakingToken = IERC20(_tokenAddress);
    }

    /**
     * @notice Agent AI zastawia tokeny, aby stać się "Verified Node"
     */
    function stake(uint256 amount) external {
        require(amount >= MIN_STAKE, "TrustLayer: Amount below minimum stake");
        require(stakingToken.transferFrom(msg.sender, address(this), amount), "TrustLayer: Transfer failed");

        stakedBalance[msg.sender] += amount;
        isVerified[msg.sender] = true;

        emit Staked(msg.sender, amount);
    }

    /**
     * @notice Agent AI wycofuje tokeny (traci status weryfikacji, jeśli spadnie poniżej minimum)
     */
    function unstake(uint256 amount) external {
        require(stakedBalance[msg.sender] >= amount, "TrustLayer: Insufficient staked balance");

        stakedBalance[msg.sender] -= amount;

        // Jeśli po wycofaniu saldo spada poniżej minimum, odbieramy certyfikat zaufania
        if (stakedBalance[msg.sender] < MIN_STAKE) {
            isVerified[msg.sender] = false;
        }

        require(stakingToken.transfer(msg.sender, amount), "TrustLayer: Transfer failed");
        emit Unstaked(msg.sender, amount);
    }

    /**
     * @notice Funkcja dla modułu Escrow do karania nieuczciwych agentów (Slashing)
     * @dev W pełnej wersji dodamy modyfikator 'onlyEscrowContract', aby nikt inny nie mógł kraść tokenów.
     */
    function slash(address agent, uint256 amount, string memory reason) external {
        require(stakedBalance[agent] >= amount, "TrustLayer: Insufficient stake to slash");

        stakedBalance[agent] -= amount;

        if (stakedBalance[agent] < MIN_STAKE) {
            isVerified[agent] = false;
        }

        // W przyszłości: zablokowane tokeny trafiają do puli nagród (Treasury) lub są spalane.
        emit Slashed(agent, amount, reason);
    }
}
